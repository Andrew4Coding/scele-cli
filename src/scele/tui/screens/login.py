from __future__ import annotations

from textual import on, work
from textual.app import ComposeResult
from textual.containers import Center, Middle, Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Label, Static

from ...auth import terminal_login
from ...session import SceleSession


class LoginScreen(Screen[None]):
    """Login screen for SCELE authentication."""

    BINDINGS = [("escape", "quit", "Quit")]

    DEFAULT_CSS = """
    LoginScreen {
        align: center middle;
    }
    #login-form {
        width: 50;
        height: auto;
        border: panel $accent;
        padding: 1 2;
        background: $surface;
    }
    #login-title {
        text-style: bold;
        text-align: center;
        width: 100%;
        color: $accent;
    }
    #login-subtitle {
        text-align: center;
        width: 100%;
        color: $text-muted;
        margin-bottom: 1;
    }
    #login-form Input {
        margin-bottom: 1;
    }
    #login-btn {
        width: 100%;
        margin-bottom: 1;
    }
    #login-status {
        text-align: center;
        width: 100%;
        color: $error;
    }
    """

    def compose(self) -> ComposeResult:
        with Middle():
            with Center():
                with Vertical(id="login-form"):
                    yield Static("SCELE TUI", id="login-title")
                    yield Static("Fasilkom UI — Moodle Client", id="login-subtitle")
                    yield Input(placeholder="Username", id="username")
                    yield Input(placeholder="Password", password=True, id="password")
                    yield Button("Login", variant="success", id="login-btn")
                    yield Label("", id="login-status")

    @on(Button.Pressed, "#login-btn")
    def handle_login(self) -> None:
        self._do_login()

    @on(Input.Submitted, "#password")
    def handle_submit(self) -> None:
        self._do_login()

    @on(Input.Submitted, "#username")
    def handle_username_submit(self) -> None:
        self.query_one("#password", Input).focus()

    def _do_login(self) -> None:
        username = self.query_one("#username", Input).value.strip()
        password = self.query_one("#password", Input).value
        if not username or not password:
            self.query_one("#login-status", Label).update("Please enter username and password")
            return
        self.query_one("#login-btn", Button).disabled = True
        self.query_one("#login-status", Label).update("Logging in...")
        self._attempt_login(username, password)

    @work(thread=True)
    def _attempt_login(self, username: str, password: str) -> None:
        try:
            # terminal_login calls sys.exit on failure, so we need to catch SystemExit
            code = terminal_login(username, password)
            if code == 0:
                self.app.session = SceleSession()
                from .dashboard import DashboardScreen

                self.app.call_from_thread(self.app.switch_screen, DashboardScreen())
            else:
                self.app.call_from_thread(self._show_error, "Login failed")
        except SystemExit:
            self.app.call_from_thread(self._show_error, "Invalid credentials")
        except Exception as e:
            self.app.call_from_thread(self._show_error, str(e))

    def _show_error(self, msg: str) -> None:
        self.query_one("#login-status", Label).update(f"[!] {msg}")
        self.query_one("#login-btn", Button).disabled = False
