from domain.tools.tool import Tool


class FunctionTool(Tool):
    type = "function"

    @staticmethod
    def is_type(tool_call):
        type = tool_call.type if hasattr(tool_call, "type") else tool_call["type"]
        return type == FunctionTool.type

    def debug(self):
        return f"""
        | type: {self.type}
            | function: {self.tool_call["function"]["name"]}
            | arguments: {self.tool_call["function"]["arguments"]}
            | outputs: {self.tool_call["function"]["outputs"] if "outputs" in self.tool_call["function"] else None}
        """
