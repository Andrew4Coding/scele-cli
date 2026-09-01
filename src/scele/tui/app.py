from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.theme import Theme
from textual.widgets import Footer, Header

from ..session import NotAuthenticatedError, SceleSession
from .settings import TuiSettings, load_settings, save_settings


CUSTOM_THEMES = (
    Theme(
        name="scele-dark",
        primary="#7dd3fc",
        secondary="#38bdf8",
        warning="#f59e0b",
        error="#fb7185",
        success="#34d399",
        accent="#fbbf24",
        foreground="#e2e8f0",
        background="#0f172a",
        surface="#1e293b",
        panel="#334155",
        dark=True,
    ),
    Theme(
        name="scele-light",
        primary="#0369a1",
        secondary="#0284c7",
        warning="#b45309",
        error="#be123c",
        success="#047857",
        accent="#b45309",
        foreground="#0f172a",
        background="#f8fafc",
        surface="#e2e8f0",
        panel="#cbd5e1",
        dark=False,
    ),
)


class SceleApp(App):
    """SCELE TUI — Interactive terminal client for SCELE (Moodle)."""

    TITLE = "SCELE TUI"
    SUB_TITLE = "Fasilkom UI"
    CSS_PATH = Path("styles/app.tcss")

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True, id="app.quit"),
        Binding("d", "toggle_dark", "Toggle Dark Mode", id="app.toggle_dark"),
        Binding("question_mark", "help", "Help", id="app.help"),
        Binding("f2", "settings", "Settings", id="app.settings"),
    ]

    def __init__(self) -> None:
        super().__init__()
        for theme in CUSTOM_THEMES:
            self.register_theme(theme)
        self.settings = load_settings()
        if self.settings.theme not in self.available_themes:
            self.settings.theme = self.theme
        self.theme = self.settings.theme
        self.set_keymap(self.settings.keymap)
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
        if self.theme in {"scele-dark", "scele-light"}:
            next_theme = "scele-light" if self.theme == "scele-dark" else "scele-dark"
        else:
            next_theme = "textual-light" if self.current_theme.dark else "textual-dark"
        self.apply_settings(TuiSettings(theme=next_theme, keymap=self.settings.keymap))

    def action_settings(self) -> None:
        from .screens.settings import SettingsScreen

        self.push_screen(SettingsScreen())

    def apply_settings(self, settings: TuiSettings) -> None:
        """Apply and persist UI preferences after the settings form confirms them."""
        if settings.theme not in self.available_themes:
            raise ValueError(f"Unknown theme: {settings.theme}")
        self.set_keymap(settings.keymap)
        self.theme = settings.theme
        self.settings = settings
        save_settings(settings)

    def action_help(self) -> None:
        """Show general help notification."""
        self.notify(
            "[b]Key Bindings:[/b]\n"
            "q: Quit  |  d: Theme  |  f2: Settings  |  r: Refresh\n"
            "Enter: Select  |  Escape: Back",
            title="Help",
            timeout=5,
        )
