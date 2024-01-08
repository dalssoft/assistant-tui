from domain.tools.tool import Tool


class CodeInterpreterTool(Tool):
    type = "code_interpreter"

    @staticmethod
    def is_type(tool_call):
        type = tool_call.type if hasattr(tool_call, "type") else tool_call["type"]
        return type == CodeInterpreterTool.type

    def debug(self):
        return f"""
        | type: {self.type}
            | input: {self.tool_call.code_interpreter.input}
            | outputs: {self.tool_call.code_interpreter.outputs}
        """
