from ast import Add
from concurrent.futures import thread
from email import message
from textual import on
from textual.containers import ScrollableContainer
from textual.widgets import Button, Static, TextArea
from textual.containers import Vertical, Container, Horizontal, Center
from textual.reactive import reactive
from textual.message import Message
from domain.message import Message as Msg
from domain.thread_run import ThreadRun
from log import log_action


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


class MessageList(ScrollableContainer):
    thread = None

    async def clear(self):
        await self.remove_children()

    async def _add_user_message(self, message):
        user_message = UserMessage(message.text(), id=message.id)
        await self.mount(user_message)
        return user_message

    async def _add_assistant_message(self, message):
        assistant_message = AssistantMessage(message.text(), id=message.id)
        await self.mount(assistant_message)
        return assistant_message

    async def fill(self, thread):
        if thread is None:
            return
        self.thread = thread
        await self.clear()
        self.loading = True
        messages = thread.retrieve_messages(order="asc")
        for message in messages:
            add_message = {
                "user": self._add_user_message,
                "assistant": self._add_assistant_message,
            }
            await add_message[message.role](message)

        self.scroll_end(animate=True, duration=0.2)
        self.loading = False

    async def retrieve_assistant_new_message(self, message_id):
        message = self.thread.retrieve_message_and_append(message_id)
        assistant_message = await self._add_assistant_message(message)
        self.scroll_to_widget(assistant_message, animate=True)

    async def new_message(self, assistant, thread, text):
        message = Msg.create(thread, text)
        ui_user_message = await self._add_user_message(message)
        ui_user_message.scroll_visible(animate=True)
        run = ThreadRun(assistant, thread)
        run.watch_for_status_change(self._on_run_completion)
        run.watch_for_new_step(self._on_new_step)
        run.create()
        await run.wait_for_completion()

    def _on_run_completion(self, thread_run):
        log_action(self, "_on_run_completion", thread_run)

    async def _on_new_step(self, thread_run_step):
        await self.retrieve_assistant_new_message(thread_run_step.message_id())


class NewMessage(ScrollableContainer):
    def compose(self):
        text_area = TextArea(id="message_textarea")
        text_area.show_line_numbers = False
        yield Horizontal(
            text_area,
            Button("Send", id="send_message_button"),
        )

    @on(Button.Pressed, "#send_message_button")
    def send_message_click(self, event):
        self.send_message()

    def send_message(self):
        text = self.query_one("#message_textarea").text
        self.post_message(self.MessageSent(text))
        self.query_one("#message_textarea").text = ""

    class MessageSent(Message):
        def __init__(self, text):
            super().__init__()
            self.text = text


class ThreadMessagesContainer(ScrollableContainer):
    assistant = reactive(None)
    thread = reactive(None)

    message_list = MessageList(id="messages")

    def compose(self):
        yield self.message_list
        yield Center(NewMessage(id="new_message"))

    async def on_new_message_message_sent(self, event):
        await self.process_new_message(event.text)

    async def process_new_message(self, text):
        await self.message_list.new_message(self.assistant, self.thread, text)

    async def watch_thread(self, thread):
        await self.fill_message_list(thread)

    async def fill_message_list(self, thread):
        if thread is None:
            return
        await self.message_list.fill(thread)
