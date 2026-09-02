from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Static

from ... import api
from ...session import NotAuthenticatedError
from ..widgets.search import FIND_BINDING, SearchableScreen, SearchBar


class ForumScreen(SearchableScreen, Screen):
    """Forum view showing discussions."""

    BINDINGS = [
        Binding("escape", "go_back", "Back", id="navigation.back"),
        Binding("backspace", "go_back", "Back", show=False),
        Binding("r", "refresh", "Refresh", id="forum.refresh"),
        Binding("n", "new_discussion", "New discussion", id="forum.new_discussion"),
        Binding("s", "subscribe", "Subscribe", id="forum.subscribe"),
        FIND_BINDING,
    ]

    search_focus = "#forum-table"

    def __init__(self, forum_id: str):
        super().__init__()
        self.forum_id = forum_id
        self._discussions = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(f"FORUM {self.forum_id}", id="forum-title")
        yield SearchBar()
        yield DataTable(id="forum-table")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#forum-table", DataTable)
        table.add_columns("ID", "Name", "Author", "Replies", "Last Post")
        table.cursor_type = "row"
        table.loading = True
        self._load_forum()

    @work(thread=True)
    def _load_forum(self) -> None:
        try:
            session = self.app.session
            discussions = api.forum(session, self.forum_id)
            self.app.call_from_thread(self._populate, discussions)
        except NotAuthenticatedError:
            self.app.call_from_thread(self.notify, "Session expired", severity="error")
        except Exception as e:
            self.app.call_from_thread(self.notify, f"Error: {e}", severity="error")

    def _populate(self, discussions) -> None:
        self._discussions = discussions
        self._render_rows()
        self.query_one("#forum-table", DataTable).loading = False
        if not discussions:
            self.notify("No discussions in this forum", severity="warning")

    def _render_rows(self) -> None:
        """Fill the table with discussions that match the active filter."""
        table = self.query_one("#forum-table", DataTable)
        table.clear()
        query = self.search_query
        for d in self._discussions:
            haystack = f"{d.id} {d.name} {d.author} {d.last_post}".lower()
            if query and query not in haystack:
                continue
            replies = str(d.replies) if d.replies is not None else "—"
            table.add_row(d.id, d.name, d.author, replies, d.last_post, key=d.id)

    def filter_list(self, query: str) -> None:
        self._render_rows()

    @on(DataTable.RowSelected, "#forum-table")
    def on_discussion_selected(self, event: DataTable.RowSelected) -> None:
        discussion_id = str(event.row_key.value)
        from .thread import ThreadScreen

        self.app.push_screen(ThreadScreen(discussion_id))

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_refresh(self) -> None:
        table = self.query_one("#forum-table", DataTable)
        table.clear()
        table.loading = True
        self._load_forum()

    def action_new_discussion(self) -> None:
        from .composer import NewDiscussionModal

        self.app.push_screen(NewDiscussionModal(self.forum_id), self._discussion_posted)

    def action_subscribe(self) -> None:
        self._subscribe()

    @work(thread=True)
    def _subscribe(self) -> None:
        try:
            ok = api.forum_subscribe(self.app.session, self.forum_id, state=True)
        except Exception as exc:  # noqa: BLE001
            self.app.call_from_thread(self.notify, f"Subscribe failed: {exc}",
                                      severity="error")
        else:
            self.app.call_from_thread(
                self.notify,
                "Subscribed to this forum" if ok else "Subscription unchanged",
                severity="information",
            )

    def _discussion_posted(self, result: dict[str, object] | None) -> None:
        if not result or not result.get("ok"):
            return
        self.notify("Discussion posted", severity="information")
        self.action_refresh()
