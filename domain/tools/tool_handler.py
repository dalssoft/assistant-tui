from domain.tools.code_interpreter import CodeInterpreterTool
from domain.tools.function import FunctionTool
from domain.tools.retrieval import RetrievalTool


class ToolHandler:
    @staticmethod
    def from_raw(tool_call):
        types = [CodeInterpreterTool, FunctionTool, RetrievalTool]
        for t in types:
            if t.is_type(tool_call):
                return t(tool_call)
