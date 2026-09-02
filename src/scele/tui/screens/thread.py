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
        Binding("escape", "go_back", "Back", id="navigation.back"),
        Binding("backspace", "go_back", "Back", show=False),
        Binding("r", "refresh", "Refresh", id="thread.refresh"),
        Binding("n", "reply", "Reply", id="thread.reply"),
    ]

    def __init__(self, discussion_id: str):
        super().__init__()
        self.discussion_id = discussion_id

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(f"THREAD {self.discussion_id}", id="thread-title")
        yield VerticalScroll(id="posts-container")
        yield Footer()

    def on_mount(self) -> None:
        self._posts = []
        self._selected_post_id: str | None = None
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
        self._posts = list(posts)
        post_ids = {post.id for post in self._posts}
        if self._selected_post_id not in post_ids:
            self._selected_post_id = self._posts[0].id if self._posts else None
        container = self.query_one("#posts-container", VerticalScroll)
        container.remove_children()
        container.loading = False
        for i, post in enumerate(posts, 1):
            container.mount(PostView(post, index=i))
        if not posts:
            container.mount(Static("[dim]No posts in this thread[/dim]"))

    def on_post_view_selected(self, message) -> None:
        self._selected_post_id = message.post.id

    def action_reply(self) -> None:
        if not self._posts:
            self.notify("There are no posts to reply to", severity="warning")
            return
        from .composer import ReplyModal

        post_id = self._selected_post_id or self._posts[0].id
        self.app.push_screen(ReplyModal(post_id), self._reply_posted)

    def _reply_posted(self, result: dict[str, object] | None) -> None:
        if not result or not result.get("ok"):
            return
        self.notify("Reply posted", severity="information")
        self.action_refresh()

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_refresh(self) -> None:
        container = self.query_one("#posts-container", VerticalScroll)
        container.remove_children()
        container.loading = True
        self._load_thread()
