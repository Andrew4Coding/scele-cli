from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header

from ..session import NotAuthenticatedError, SceleSession


class SceleApp(App):
    """SCELE TUI — Interactive terminal client for SCELE (Moodle)."""

    TITLE = "SCELE TUI"
    SUB_TITLE = "Fasilkom UI"
    CSS_PATH = Path("styles/app.tcss")

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("d", "toggle_dark", "Toggle Dark Mode"),
        Binding("question_mark", "help", "Help"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.session: SceleSession | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        """Check auth state and show appropriate screen."""
        self.session = SceleSession()
        self._check_auth()

    @work(thread=True)
    def _check_auth(self) -> None:
        """Verify authentication in a background worker thread."""
        try:
            authenticated = self.session.is_authenticated() if self.session else False
        except (NotAuthenticatedError, Exception):
            authenticated = False

        if authenticated:
            from .screens.dashboard import DashboardScreen

            self.app.call_from_thread(self.push_screen, DashboardScreen())
        else:
            from .screens.login import LoginScreen

            self.app.call_from_thread(self.push_screen, LoginScreen())

    def action_toggle_dark(self) -> None:
        """Toggle between dark and light themes."""
        self.theme = "textual-light" if self.theme == "textual-dark" else "textual-dark"

    def action_help(self) -> None:
        """Show general help notification."""
        self.notify(
            "[b]Key Bindings:[/b]\n"
            "q: Quit  |  d: Dark Mode  |  r: Refresh\n"
            "Enter: Select  |  Escape: Back",
            title="Help",
            timeout=5,
        )
