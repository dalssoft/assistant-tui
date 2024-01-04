from domain.tools.tool import Tool


class CodeInterpreterTool(Tool):
    type = "code_interpreter"

    @staticmethod
    def is_type(tool_call):
        return tool_call.type == CodeInterpreterTool.type

    def debug(self):
        return f"""
        | type: {self.type}
            | input: {self.tool_call.code_interpreter.input}
            | outputs: {self.tool_call.code_interpreter.outputs}
        """
