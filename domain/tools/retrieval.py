from domain.tools.tool import Tool


class RetrievalTool(Tool):
    type = "retrieval"

    @staticmethod
    def is_type(tool_call):
        return tool_call.type == RetrievalTool.type

    def debug(self):
        retrieval = (
            self.tool_call.retrieval.retrieval if self.tool_call.retrieval else None
        )
        return f"""
        | type: {self.type}
            | retrieval: {retrieval}
        """
