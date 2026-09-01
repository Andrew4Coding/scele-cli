from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from ... import api
from ...session import NotAuthenticatedError
from ..widgets.post_view import PostView


class ThreadScreen(Screen):
    """Thread view showing posts in a discussion."""

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("backspace", "go_back", "Back", show=False),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self, discussion_id: str):
        super().__init__()
        self.discussion_id = discussion_id

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(f"🧵 Thread {self.discussion_id}", id="thread-title")
        yield VerticalScroll(id="posts-container")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#posts-container").loading = True
        self._load_thread()

    @work(thread=True)
    def _load_thread(self) -> None:
        try:
            session = self.app.session
            posts = api.thread(session, self.discussion_id)
            self.app.call_from_thread(self._populate, posts)
        except NotAuthenticatedError:
            self.app.call_from_thread(self.notify, "Session expired", severity="error")
        except Exception as e:
            self.app.call_from_thread(self.notify, f"Error: {e}", severity="error")

    def _populate(self, posts) -> None:
        container = self.query_one("#posts-container", VerticalScroll)
        container.remove_children()
        container.loading = False
        for i, post in enumerate(posts, 1):
            container.mount(PostView(post, index=i))
        if not posts:
            container.mount(Static("[dim]No posts in this thread[/dim]"))

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_refresh(self) -> None:
        container = self.query_one("#posts-container", VerticalScroll)
        container.remove_children()
        container.loading = True
        self._load_thread()
