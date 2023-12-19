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
        )

    def watch_assistant(self, assistant):
        thread_list_container = self.query_one("#thread_list_container")
        thread_list_container.assistant = assistant
        thread_messages_container = self.query_one("#thread_messages_container")
        thread_messages_container.assistant = assistant

    def on_thread_list_container_thread_selected(self, event):
        thread_messages_container = self.query_one("#thread_messages_container")
        thread_messages_container.thread = event.thread
