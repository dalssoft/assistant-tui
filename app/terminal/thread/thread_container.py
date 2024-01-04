from textual.containers import Container, Horizontal
from textual.reactive import reactive
from app.terminal.thread.thread_list import ThreadListContainer
from app.terminal.thread.thread_messages import ThreadMessagesContainer


class ThreadContainer(Container):
    assistant = reactive(None)

    def compose(self):
        yield Horizontal(
            ThreadListContainer(id="thread_list_container"),
            ThreadMessagesContainer(id="thread_messages_container"),
            id="thread_container_inner",
        )

    def watch_assistant(self, assistant):
        thread_list_container = self.query_one("#thread_list_container")
        thread_list_container.assistant = assistant
        thread_messages_container = self.query_one("#thread_messages_container")
        thread_messages_container.assistant = assistant

    async def on_thread_list_container_thread_selected(self, event):
        thread_messages_container_old = self.query_one("#thread_messages_container")
        await thread_messages_container_old.remove()

        thread_messages_container = ThreadMessagesContainer(
            id="thread_messages_container"
        )

        thread_container = self.query_one("#thread_container_inner")
        await thread_container.mount(thread_messages_container)
        thread_messages_container.assistant = self.assistant
        thread_messages_container.thread = event.thread
