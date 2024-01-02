from ast import Add
from concurrent.futures import thread
from email import message
from textual import on
from textual.containers import ScrollableContainer
from textual.widgets import Button, Static, TextArea, Checkbox
from textual.containers import Vertical, Container, Horizontal, Center
from textual.reactive import reactive
from textual.message import Message
from domain.message import Message as Msg
from domain.thread_run import ThreadRun
from log import log_action
import time


class ThreadMessage(Container):
    avatar = ""
    container_classes = ""
    title = ""

    def __init__(self, text, **kwargs):
        self.text = text
        super().__init__(**kwargs)

    def compose(self):
        message = Static(self.text, classes="message")
        message.border_title = self.title
        yield Container(
            Static(self.avatar, classes="avatar"),
            message,
            classes=self.container_classes,
            id="message_container",
        )


class AssistantMessage(ThreadMessage):
    def compose(self):
        self.avatar = "🤖 Assistant"
        self.title = ""
        self.container_classes = "assistant"
        yield from super().compose()


class UserMessage(ThreadMessage):
    def compose(self):
        self.avatar = "👤 You"
        self.title = ""
        self.container_classes = "user"
        yield from super().compose()


class DebugMessage(ThreadMessage):
    def compose(self):
        self.avatar = f"🐞 Debug"
        self.title = ""
        self.container_classes = "debug"
        yield from super().compose()


class MessageList(ScrollableContainer):
    thread = None

    async def clear(self):
        await self.remove_children()

    async def add_user_message(self, message):
        user_message = UserMessage(message.text(), id=message.id)
        await self.mount(user_message)
        return user_message

    async def add_assistant_message(self, message):
        assistant_message = AssistantMessage(message.text(), id=message.id)
        await self.mount(assistant_message)
        return assistant_message

    async def add_debug_message(self, text):
        current_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        text = f"{text}\n{current_date}"
        debug_message = DebugMessage(text)
        await self.mount(debug_message)
        return debug_message

    async def fill(self, thread):
        if thread is None:
            return
        self.thread = thread
        await self.clear()
        self.loading = True
        messages = thread.retrieve_messages(order="asc")
        for message in messages:
            add_message = {
                "user": self.add_user_message,
                "assistant": self.add_assistant_message,
            }
            await add_message[message.role](message)

        self.scroll_end(animate=True, duration=0.2)
        self.loading = False


class NewMessage(ScrollableContainer):
    def compose(self):
        text_area = TextArea(id="message_textarea")
        text_area.show_line_numbers = False
        yield Horizontal(
            Checkbox("Debug", id="debug_checkbox"),
            text_area,
            Button("Send", id="send_message_button"),
            classes="new_message_container",
        )

    @on(Button.Pressed, "#send_message_button")
    def send_message_click(self, event):
        self.send_message()

    def send_message(self):
        text = self.query_one("#message_textarea").text
        self.post_message(self.MessageSent(text))
        self.query_one("#message_textarea").text = ""

    @on(Checkbox.Changed, "#debug_checkbox")
    def debug_checkbox_changed(self, event):
        self.post_message(self.DebugChanged(event.checkbox.value))

    class MessageSent(Message):
        def __init__(self, text):
            super().__init__()
            self.text = text

    class DebugChanged(Message):
        def __init__(self, debug):
            super().__init__()
            self.debug = debug


class ThreadMessagesContainer(ScrollableContainer):
    assistant = reactive(None)
    thread = reactive(None)
    is_debug = reactive(False)

    message_list = MessageList(id="messages")

    def compose(self):
        yield self.message_list
        yield Center(NewMessage(id="new_message"))

    async def on_new_message_message_sent(self, event):
        await self.new_message(self.assistant, self.thread, event.text)

    async def on_new_message_debug_changed(self, event):
        self.is_debug = event.debug

    async def watch_thread(self, thread):
        await self.fill_message_list(thread)

    async def fill_message_list(self, thread):
        if thread is None:
            return
        await self.message_list.fill(thread)

    async def new_message(self, assistant, thread, text):
        button = self.query_one("#send_message_button")
        button.loading = True
        button.disabled = True
        message = Msg.create(thread, text)
        ui_user_message = await self.message_list.add_user_message(message)
        ui_user_message.scroll_visible(animate=True)
        run = ThreadRun(assistant, thread)
        run.watch_for_status_change(self._on_status_change)
        run.watch_for_new_step(self._on_new_step)
        run.watch_for_new_step_completed(self._on_new_step_completed)
        await run.create()
        await run.wait_for_completion()

    async def _on_status_change(self, thread_run):
        if self.is_debug:
            await self.message_list.add_debug_message(
                f"""Run status changed
                | id: {thread_run.id}
                | status: {thread_run.status}
                """
            )

    async def _on_new_step(self, thread_run_step):
        if self.is_debug:
            await self.message_list.add_debug_message(
                f"""New step 
                {thread_run_step.debug()}
                """
            )

    async def _on_new_step_completed(self, thread_run_step):
        if self.is_debug:
            await self.message_list.add_debug_message(
                f"""New step completed
                {thread_run_step.debug()}
                """
            )
        if thread_run_step.type == "message_creation":
            await self.retrieve_assistant_new_message(thread_run_step.message_id())

    async def retrieve_assistant_new_message(self, message_id):
        message = self.thread.retrieve_message_and_append(message_id)
        await self.message_list.add_assistant_message(message)
        self.message_list.scroll_end(animate=True, duration=0.2)
        button = self.query_one("#send_message_button")
        button.loading = False
        button.disabled = False
