from textual import on
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Header, Footer, Static, Select, Label, Button
from textual.containers import Horizontal, Vertical, Middle, Center
from textual.message import Message
from domain.assistant import Assistant
from log import log_action


class PlaceholderWithLabel(Static):
    def __init__(self, label, placeholder_id, placeholder_text, classes="singleline"):
        self.label = label
        self.placeholder_id = placeholder_id
        self.placeholder_text = placeholder_text
        super().__init__(classes=classes)

    def compose(self) -> ComposeResult:
        yield Label(self.label, classes="label")
        yield Label(
            self.placeholder_text, id=self.placeholder_id, classes="placeholder"
        )


class AssistantContainer(ScrollableContainer):
    assistants = []
    assistant = None

    def on_mount(self):
        self.list_all_assistants()

    @on(Select.Changed, "#assistant_name")
    def assistant_name_select_changed(self, event):
        self.select_assistant(event.value)

    @on(Button.Pressed, "#use_assistant")
    def use_assistant_button_clicked(self, event):
        event.stop()
        self.use_assistant()

    def list_all_assistants(self):
        self.assistants = Assistant.list_all()
        assistants = list(
            (assistant.name, assistant.id) for assistant in self.assistants
        )
        # assistants = [("assistant1", "1"), ("assistant2", "2")]
        self.query_one("#assistant_name").set_options(assistants)
        log_action(self, "list_all_assistants", self.assistants)

    def select_assistant(self, assistant_id):
        assistant = next(
            (assistant for assistant in self.assistants if assistant.id == assistant_id)
        )
        self.assistant = assistant
        inner_assistant = assistant.assistant
        self.query_one("#instructions").update(inner_assistant.instructions)
        self.query_one("#model").update(inner_assistant.model)
        self.query_one("#tools").update(
            ", ".join(list(tool.type for tool in inner_assistant.tools))
        )
        self.query_one("#files").update(str(inner_assistant.file_ids))
        log_action(self, "select_assistant", assistant)

    def use_assistant(self):
        self.add_class("assistant_selected")
        self.post_message(self.AssistantSelected(self.assistant))
        log_action(self, "use_assistant", self.assistant)

    def compose(self) -> ComposeResult:
        yield Select(
            options=self.assistants,
            id="assistant_name",
            prompt="Select an assistant",
        )
        yield PlaceholderWithLabel(
            "Instructions:",
            "instructions",
            "As a bakery assistant...",
            classes="multiline",
        )
        yield PlaceholderWithLabel("Model:", "model", "gpt4")
        yield PlaceholderWithLabel("Tools:", "tools", "code_interpreter")
        yield PlaceholderWithLabel("Files:", "files", "file1")
        yield Center(Button("Use this assistant", id="use_assistant"))

    class AssistantSelected(Message):
        def __init__(self, assistant):
            super().__init__()
            self.assistant = assistant
