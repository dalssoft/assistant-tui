from log import log_action
from openai import OpenAI
from threading import Thread
from domain.steps.step_list import StepList
from domain.steps.message_creation import MessageCreationStep
import time
import asyncio


class Run:
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

    def __init__(self, assistant, thread, id=None):
        self.client = OpenAI()
        self.assistant = assistant
        self.thread = thread
        self.id = id
        self.thread_run = None
        self.step_list = StepList(self)
        self.step_list.watch_for_new_step(self._on_new_step)
        self.status = self.run_status["queued"]
        self.callbacks = {
            "status_change": [],
            "new_step": [],
            "step_status_change": [],
        }

    async def _update_from_raw(self, thread_run):
        self.thread_run = thread_run
        previous_status = self.status
        self.status = thread_run.status
        if previous_status != self.status:
            await self._on_status_change()

    async def create(self):
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
        )
        self.id = run.id
        await self._update_from_raw(run)

        log_action(self, "create", run)

        return self

    async def refresh(self):
        run = self.client.beta.threads.runs.retrieve(
            thread_id=self.thread.id,
            run_id=self.id,
        )
        self.thread_run = run
        await self._update_from_raw(run)

        log_action(self, "refresh", run)

        return self

    async def cancel(self):
        run = self.client.beta.threads.runs.cancel(
            thread_id=self.thread.id,
            run_id=self.id,
        )
        await self._update_from_raw(run)

        log_action(self, "cancel", run)

        return self

    def watch_for_status_change(self, callback):
        self.callbacks["status_change"].append(callback)

    async def _on_status_change(self):
        for callback in self.callbacks["status_change"]:
            await callback(self)

    def watch_for_new_step(self, callback):
        self.callbacks["new_step"].append(callback)

    def watch_for_step_status_change(self, callback):
        self.callbacks["step_status_change"].append(callback)

    async def _on_new_step(self, new_step):
        for callback in self.callbacks["new_step"]:
            await callback(new_step)

        for callback in self.callbacks["step_status_change"]:
            new_step.watch_for_status_change(callback)

        await new_step.wait_for_completion()

        if isinstance(new_step, MessageCreationStep) and new_step.has_completed():
            await self.thread.retrieve_message_and_append(new_step.message_id())

    async def wait_for_completion(self):
        thread = Thread(target=asyncio.run, args=(self._polling(),))
        thread.start()
        # await self._polling()

    async def _polling(self):
        run_status_to_watch = [
            self.run_status["queued"],
            self.run_status["in_progress"],
            self.run_status["requires_action"],
            self.run_status["cancelling"],
        ]

        while self.status in run_status_to_watch:
            log_action(self, "_polling")
            await self.refresh()
            await self.step_list.refresh()
            time.sleep(0.1)
