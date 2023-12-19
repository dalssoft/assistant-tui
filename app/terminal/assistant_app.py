from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from log import log_action
from app.terminal.assistant_container import AssistantContainer
from app.terminal.thread.thread_container import ThreadContainer


class AppState:
    assistant = None
    thread = None


class AssistantApp(App):
    CSS_PATH = "app.css"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode"), ("q", "quit", "Quit")]
    TITLE = "Assistant Terminal 🤖"

    app_state = AppState()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield AssistantContainer(id="assistant_container")
        yield ThreadContainer(id="thread_container", classes="remove")

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_quit(self) -> None:
        """An action to quit the app."""
        self.exit()

    def on_assistant_container_assistant_selected(self, event):
        self.app_state.assistant = event.assistant
        self.query_one("#assistant_container").display = False
        thread_container = self.query_one("#thread_container")
        thread_container.display = True
        thread_container.assistant = event.assistant
        log_action(self, "on_assistant_container_assistant_selected", event.assistant)


if __name__ == "__main__":
    app = AssistantApp()
    app.run()
