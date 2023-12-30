from concurrent.futures import thread
from textual import on
from textual.containers import ScrollableContainer
from textual.widgets import Header, Footer, Label, ListView, ListItem, Button, Static
from textual.containers import Vertical, Container
from textual.reactive import reactive
from textual.message import Message
from domain.thread_list import ThreadList
from log import log_action


class ThreadListContainer(ScrollableContainer):
    assistant = reactive(None)
    threads = reactive([])
    current_thread = reactive(None)

    def compose(self):
        yield Vertical(
            Static(id="assistant_name"),
            Label("Threads:"),
            ListView(id="thread_list"),
            Button("Create Thread", id="create_thread_button"),
        )

    @on(Button.Pressed, "#create_thread_button")
    def create_thread_click(self, event):
        self.create_thread()

    @on(ListView.Selected, "#thread_list")
    def thread_list_selected(self, event):
        self.select_thread(event.item.id)

    def watch_assistant(self, assistant):
        self.update_assistant(assistant)
        self.list_all_threads(assistant)

    def watch_threads(self, threads):
        self.update_threads_list(threads)

    def watch_current_thread(self, thread):
        self.post_message(self.ThreadSelected(thread))
        log_action(self, "watch_current_thread", thread)

    def update_assistant(self, assistant):
        if assistant is None:
            return
        self.query_one("#assistant_name").update(assistant.name)

    def update_threads_list(self, threads):
        if not threads:
            return
        list_view = self.query_one("#thread_list")
        list_view.clear()
        for thread in threads:
            list_view.append(ListItem(Label(thread.name), id=thread.id))

        log_action(self, "list_all_threads")

    def list_all_threads(self, assistant):
        if assistant is None:
            return
        self.threads = ThreadList(assistant.id).list_all()
        log_action(self, "list_all_threads")

    def create_thread(self):
        thread_name = "New Thread - " + str(len(self.threads) + 1)
        self.current_thread = ThreadList(self.assistant.id).create_thread(thread_name)
        self.list_all_threads(self.assistant)
        list = self.query_one("#thread_list")
        items = list.children
        for index, item in enumerate(items):
            if item.id == self.current_thread.id:
                list.index = index

        log_action(self, "create_thread")

    def select_thread(self, thread_id):
        self.current_thread = next(
            (thread for thread in self.threads if thread.id == thread_id)
        )
        log_action(self, "select_thread")

    class ThreadSelected(Message):
        def __init__(self, thread):
            super().__init__()
            self.thread = thread
