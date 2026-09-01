from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from ... import api
from ...session import NotAuthenticatedError


class AnnouncementsScreen(Screen):
    """Full announcements view."""

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("backspace", "go_back", "Back", show=False),
        Binding("r", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("📢 Announcements", id="announcements-title")
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
        container = self.query_one("#announcements-list", VerticalScroll)
        container.remove_children()
        container.loading = False

        if not announcements:
            container.mount(Static("[dim]No announcements[/dim]"))
            return

        for i, ann in enumerate(announcements, 1):
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

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_refresh(self) -> None:
        container = self.query_one("#announcements-list", VerticalScroll)
        container.remove_children()
        container.loading = True
        self._load_announcements()
