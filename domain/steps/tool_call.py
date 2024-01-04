from json import tool
from domain.steps.step import Step
from domain.tools.tool_handler import ToolHandler


class ToolCallStep(Step):
    type = "tool_calls"

    def __init__(self, thread_run, thread_run_step):
        super().__init__(thread_run, thread_run_step.id)
        self.tool_calls = thread_run_step.step_details.tool_calls

    @staticmethod
    def is_type(step):
        return step.step_details.type == ToolCallStep.type

    def debug(self):
        tools = [ToolHandler.from_raw(tool_call) for tool_call in self.tool_calls]
        debugs = [tool.debug() for tool in tools]
        return (
            super().debug()
            + f"""
        | tool_calls: {"".join(debugs)}
        """
        )
