from re import T
from log import log_action
from openai import OpenAI
from threading import Thread
from domain.thread_run_step import ThreadRunStep
import time


class ThreadRunStepList:
    def __init__(self, thread_run):
        self.client = OpenAI()
        self.thread_run = thread_run
        self.steps = []
        self.callbacks = {
            "new_step": [],
        }

    async def retrieve(self):
        steps = self.client.beta.threads.runs.steps.list(
            thread_id=self.thread_run.thread.id,
            run_id=self.thread_run.id,
        )

        for step in steps.data:
            if step.id not in [s.id for s in self.steps]:
                new_step = ThreadRunStep.from_raw(self.thread_run, step)
                await self._add_new_step(new_step)

        log_action(self, "retrieve", steps)

        return self

    def watch_for_new_step(self, callback):
        self.callbacks["new_step"].append(callback)

    async def _add_new_step(self, new_step):
        self.steps.append(new_step)
        for callback in self.callbacks["new_step"]:
            await callback(new_step)
