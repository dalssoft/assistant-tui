from domain.steps.message_creation import MessageCreationStep
from domain.steps.tool_call import ToolCallStep


class StepHandler:
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
