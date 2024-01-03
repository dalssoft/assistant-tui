from log import log_action
from openai import OpenAI
from threading import Thread
import time


class ThreadRunStep:
    run_status = {
        "in_progress": "in_progress",
        "cancelled": "cancelled",
        "failed": "failed",
        "completed": "completed",
        "expired": "expired",
    }

    time_to_wait = 1
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

    def retrieve(self):
        step = self.client.beta.threads.runs.steps.retrieve(
            thread_id=self.thread_run.thread.id,
            run_id=self.thread_run.id,
            step_id=self.id,
        )
        self.thread_run_step = step
        self.status = step.status
        self.type = step.step_details.type
        log_action(self, "retrieve", step)
        return self

    @staticmethod
    def from_raw(thread_run, thread_run_step):
        types = [MessageCreationStep, ToolCallStep]
        step = None
        for type in types:
            if type.is_type(thread_run_step):
                step = type(thread_run, thread_run_step)
                break
        step.thread_run_step = thread_run_step
        step.status = thread_run_step.status
        return step

    def wait_for_completion(self):
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
            self.retrieve()

            # handle status change
            if self.status != previous_status:
                previous_status = self.status
                self._on_status_change()

            # wait for next iteration
            time.sleep(self.time_to_wait)

        return self

    def watch_for_status_change(self, callback):
        self.callbacks["status_change"].append(callback)

    def _on_status_change(self):
        for callback in self.callbacks["status_change"]:
            callback(self)

    def debug(self):
        return f"""
        | id: {self.id}
        | status: {self.status}
        | type: {self.thread_run_step.step_details.type}"""


class MessageCreationStep(ThreadRunStep):
    type = "message_creation"

    def __init__(self, thread_run, thread_run_step):
        super().__init__(thread_run, thread_run_step.id)
        self.thread_run_step = thread_run_step

    @staticmethod
    def is_type(step):
        return step.step_details.type == MessageCreationStep.type

    def message_id(self):
        return self.thread_run_step.step_details.message_creation.message_id

    def debug(self):
        return (
            super().debug()
            + f"""        
        | message_id: {self.message_id()}
        """
        )


class ToolCallStep(ThreadRunStep):
    type = "tool_calls"

    def __init__(self, thread_run, thread_run_step):
        super().__init__(thread_run, thread_run_step.id)
        thread_run_step = thread_run_step
        self.tool_calls = thread_run_step.step_details.tool_calls

    @staticmethod
    def is_type(step):
        return step.step_details.type == ToolCallStep.type

    def debug(self):
        def code_interpreter_debug(tool_call):
            if tool_call.type != "code_interpreter":
                return ""
            return f"""
            | input: {tool_call.code_interpreter.input}
            | outputs: {tool_call.code_interpreter.outputs}
            """

        def retrieval_debug(tool_call):
            if tool_call.type != "retrieval":
                return ""
            retrieval = tool_call.retrieval.retrieval if tool_call.retrieval else None
            return f"""
            | retrieval: {retrieval}
            """

        def function_debug(tool_call):
            if tool_call.type != "function":
                return ""
            return f"""
            | name: {tool_call.function.name}
            | args: {tool_call.function.arguments}
            | output: {tool_call.function.output}
            """

        debugs = []
        for tool_call in self.tool_calls:
            debugs.append(
                f"""
            | type: {tool_call.type}"""
                + code_interpreter_debug(tool_call)
                + retrieval_debug(tool_call)
                + function_debug(tool_call)
            )

        return (
            super().debug()
            + f"""
        | tool_calls: {"".join(debugs)}
        """
        )
