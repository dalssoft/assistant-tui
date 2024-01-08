from os import name
from typing import Container
from textual import on
from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer, Container
from textual.widgets import Header, Footer, Static, Select, Label, Button, Switch
from textual.containers import Horizontal, Vertical, Middle, Center
from textual.message import Message
from domain.assistant import Assistant
from log import log_action
from textual.reactive import reactive
import webbrowser


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


class ToolSwitch(Horizontal):
    value = reactive(False)
    switch = None

    def __init__(self, label, id):
        self.label = label
        super().__init__(id=id)

    def compose(self):
        self.switch = Switch(value=self.value, disabled=True)
        yield self.switch
        yield Middle(Static(self.label))

    def watch_value(self, value):
        if self.switch is None:
            return
        self.switch.value = value


class AssistantContainer(ScrollableContainer):
    assistants = []
    assistant = None

    def compose(self) -> ComposeResult:
        yield Select(
            options=self.assistants,
            id="assistant_name",
            prompt="Select an assistant",
        )
        with Vertical(id="empty_details"):
            link = "https://platform.openai.com/assistants"
            yield Center(Static("[b]Assistant Text User Interface[/b]"))
            yield Static("Select an existing assistant from the list above.")
            yield Static(
                f"Or you can create an assistant using the OpenAI platform on the web: {link}"
            )

        with Vertical(id="assistant_details", classes="remove"):
            yield PlaceholderWithLabel(
                "Instructions:",
                "instructions",
                "...",
                classes="multiline",
            )
            yield PlaceholderWithLabel("Model:", "model", "")
            yield Vertical(
                Label("Tools:", classes="label"),
                ToolSwitch(
                    "Code Interpreter",
                    id="code_interpreter",
                ),
                ToolSwitch(
                    "Retrival",
                    id="retrieval",
                ),
                ToolSwitch(
                    "Function",
                    id="function",
                ),
                PlaceholderWithLabel("Functions:", "functions", ""),
                classes="tools",
            )
            yield PlaceholderWithLabel("Files:", "files", "")
            yield Center(Button("Use this assistant", id="use_assistant"))

    def action_open_url(self, url):
        webbrowser.open(url)

    def on_mount(self):
        self.list_all_assistants()

    @on(Select.Changed, "#assistant_name")
    def assistant_name_select_changed(self, event):
        empty_details = self.query_one("#empty_details")
        empty_details.add_class("remove")
        assistant_details = self.query_one("#assistant_details")
        assistant_details.remove_class("remove")
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
        self.query_one("#code_interpreter").value = any(
            tool.type == "code_interpreter" for tool in inner_assistant.tools
        )
        self.query_one("#retrieval").value = any(
            tool.type == "retrieval" for tool in inner_assistant.tools
        )
        self.query_one("#function").value = any(
            tool.type == "function" for tool in inner_assistant.tools
        )
        functions = list(
            tool.function.name
            for tool in inner_assistant.tools
            if tool.type == "function"
        )
        self.query_one("#functions").update(", ".join(functions))

        self.query_one("#files").update(", ".join(inner_assistant.file_ids))
        log_action(self, "select_assistant", assistant)

    def use_assistant(self):
        self.add_class("assistant_selected")
        self.post_message(self.AssistantSelected(self.assistant))
        log_action(self, "use_assistant", self.assistant)

    class AssistantSelected(Message):
        def __init__(self, assistant):
            super().__init__()
            self.assistant = assistant
