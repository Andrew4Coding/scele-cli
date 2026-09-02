from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from ... import api
from ...session import NotAuthenticatedError
from ..widgets.search import FIND_BINDING, SearchableScreen, SearchBar


class AnnouncementsScreen(SearchableScreen, Screen):
    """Full announcements view."""

    BINDINGS = [
        Binding("escape", "go_back", "Back", id="navigation.back"),
        Binding("backspace", "go_back", "Back", show=False),
        Binding("r", "refresh", "Refresh", id="announcements.refresh"),
        FIND_BINDING,
    ]

    search_focus = "#announcements-list"

    def __init__(self) -> None:
        super().__init__()
        self._announcements = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("ANNOUNCEMENTS", id="announcements-title")
        yield SearchBar()
        yield VerticalScroll(id="announcements-list")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#announcements-list").loading = True
        self._load_announcements()

    @work(thread=True)
    def _load_announcements(self) -> None:
        try:
            session = self.app.session
            announcements = api.announcements(session)
            self.app.call_from_thread(self._populate, announcements)
        except NotAuthenticatedError:
            self.app.call_from_thread(self.notify, "Session expired", severity="error")
        except Exception as e:
            self.app.call_from_thread(self.notify, f"Error: {e}", severity="error")

    def _populate(self, announcements) -> None:
        self._announcements = announcements
        self.query_one("#announcements-list", VerticalScroll).loading = False
        self._render_cards()

    def _render_cards(self) -> None:
        """Show announcement cards that match the active filter."""
        container = self.query_one("#announcements-list", VerticalScroll)
        container.remove_children()
        query = self.search_query
        items = [
            ann
            for ann in self._announcements
            if not query
            or query in f"{ann.subject} {ann.author} {ann.body}".lower()
        ]

        if not items:
            empty = "[dim]No announcements[/dim]" if not query else "[dim]No matches[/dim]"
            container.mount(Static(empty))
            return

        for i, ann in enumerate(items, 1):
            # Build announcement card content
            card_content = (
                f"[b]#{i}. {ann.subject}[/b]\n"
                f"[yellow]{ann.author}[/yellow]  [dim]{ann.date}[/dim]\n"
                f"{'─' * 40}\n"
                f"{ann.body or '[dim](no body)[/dim]'}"
            )
            if ann.permalink:
                card_content += f"\n[dim]{ann.permalink}[/dim]"

            container.mount(
                Static(card_content, classes="announcement-card")
            )

    def filter_list(self, query: str) -> None:
        self._render_cards()

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_refresh(self) -> None:
        container = self.query_one("#announcements-list", VerticalScroll)
        container.remove_children()
        container.loading = True
        self._load_announcements()
