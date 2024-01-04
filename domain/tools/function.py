from domain.tools.tool import Tool


class FunctionTool(Tool):
    type = "function"

    @staticmethod
    def is_type(tool_call):
        return tool_call.type == FunctionTool.type

    def debug(self):
        return f"""
        | type: {self.type}
            | function: {self.tool_call.function.function}
            | inputs: {self.tool_call.function.inputs}
            | outputs: {self.tool_call.function.outputs}
        """
