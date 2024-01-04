from log import log_action
from openai import OpenAI
import time


class Step:
    run_status = {
        "in_progress": "in_progress",
        "cancelled": "cancelled",
        "failed": "failed",
        "completed": "completed",
        "expired": "expired",
    }

    time_to_wait = 0.1
    time_to_timeout = 120

    def __init__(self, thread_run, id=None):
        self.client = OpenAI()
        self.thread_run = thread_run
        self.id = id
        self.thread_run_step = None
        self.status = self.run_status["in_progress"]
        self.callbacks = {
            "status_change": [],
        }

    def refresh(self):
        step = self.client.beta.threads.runs.steps.retrieve(
            thread_id=self.thread_run.thread.id,
            run_id=self.thread_run.id,
            step_id=self.id,
        )
        self.thread_run_step = step
        self.status = step.status
        self.type = step.step_details.type
        log_action(self, "refresh", step)
        return self

    async def wait_for_completion(self):
        start_time = time.time()
        previous_status = self.status
        while self.status == self.run_status["in_progress"]:
            # handle timeout
            is_timeout = time.time() - start_time > self.time_to_timeout
            if is_timeout:
                self.status = self.run_status["expired"]
                log_action(self, "timeout")
                break

            # retrieve and check status
            self.refresh()

            # handle status change
            if self.status != previous_status:
                previous_status = self.status
                await self._on_status_change()

            # wait for next iteration
            time.sleep(self.time_to_wait)

        return self

    def has_completed(self):
        return self.status != self.run_status["in_progress"]

    def watch_for_status_change(self, callback):
        self.callbacks["status_change"].append(callback)

    async def _on_status_change(self):
        for callback in self.callbacks["status_change"]:
            await callback(self)

    def debug(self):
        return f"""
        | id: {self.id}
        | status: {self.status}
        | type: {self.thread_run_step.step_details.type}"""
