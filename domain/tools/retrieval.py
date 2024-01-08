from domain.tools.tool import Tool


class RetrievalTool(Tool):
    type = "retrieval"

    @staticmethod
    def is_type(tool_call):
        type = tool_call.type if hasattr(tool_call, "type") else tool_call["type"]
        return type == RetrievalTool.type

    def debug(self):
        retrieval = (
            self.tool_call.retrieval.retrieval if self.tool_call.retrieval else None
        )
        return f"""
        | type: {self.type}
            | retrieval: {retrieval}
        """
