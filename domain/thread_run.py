from log import log_action
from openai import OpenAI
from threading import Thread
from domain.thread_run_step_list import ThreadRunStepList
import time
import asyncio


class ThreadRun:
    run_status = {
        "queued": "queued",
        "in_progress": "in_progress",
        "requires_action": "requires_action",
        "cancelling": "cancelling",
        "cancelled": "cancelled",
        "failed": "failed",
        "completed": "completed",
        "expired": "expired",
    }

    run_status_to_watch = [
        run_status["queued"],
        run_status["in_progress"],
        run_status["requires_action"],
        run_status["cancelling"],
    ]

    def __init__(self, assistant, thread, id=None):
        self.client = OpenAI()
        self.assistant = assistant
        self.thread = thread
        self.id = id
        self.thread_run = None
        self.stepList = ThreadRunStepList(self)
        self.stepList.watch_for_new_step(self._on_new_step)
        self.status = self.run_status["queued"]
        self.callbacks = {
            "status_change": [],
            "new_step": [],
        }

    def _update_from_raw(self, thread_run):
        self.thread_run = thread_run
        previous_status = self.status
        self.status = thread_run.status
        if previous_status != self.status:
            self._on_status_change()

    def create(self):
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
        )
        self.id = run.id
        self._update_from_raw(run)

        log_action(self, "create", run)

        return self

    def retrieve(self):
        run = self.client.beta.threads.runs.retrieve(
            thread_id=self.thread.id,
            run_id=self.id,
        )
        self.thread_run = run
        self._update_from_raw(run)

        log_action(self, "retrieve", run)

        return self

    def cancel(self):
        run = self.client.beta.threads.runs.cancel(
            thread_id=self.thread.id,
            run_id=self.id,
        )
        self._update_from_raw(run)

        log_action(self, "cancel", run)

        return self

    def watch_for_status_change(self, callback):
        self.callbacks["status_change"].append(callback)

    def _on_status_change(self):
        for callback in self.callbacks["status_change"]:
            callback(self)

    def watch_for_new_step(self, callback):
        self.callbacks["new_step"].append(callback)

    async def _on_new_step(self, new_step):
        new_step.wait_for_completion()
        for callback in self.callbacks["new_step"]:
            await callback(new_step)

    async def wait_for_completion(self):
        thread = Thread(target=asyncio.run, args=(self._pooling(),))
        thread.start()

    async def _pooling(self):
        log_action(self, "_pooling")

        while self.status in self.run_status_to_watch:
            self.retrieve()
            await self.stepList.retrieve()
            time.sleep(2)
