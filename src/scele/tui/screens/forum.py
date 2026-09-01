from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Static

from ... import api
from ...session import NotAuthenticatedError


class ForumScreen(Screen):
    """Forum view showing discussions."""

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("backspace", "go_back", "Back", show=False),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self, forum_id: str):
        super().__init__()
        self.forum_id = forum_id

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(f"💬 Forum {self.forum_id}", id="forum-title")
        yield DataTable(id="forum-table")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#forum-table", DataTable)
        table.add_columns("ID", "Name", "Author", "Replies", "Last Post")
        table.cursor_type = "row"
        table.loading = True
        self._discussions = []  # Store discussions for lookup
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
        table = self.query_one("#forum-table", DataTable)
        table.clear()
        for d in discussions:
            replies = str(d.replies) if d.replies is not None else "—"
            table.add_row(d.id, d.name, d.author, replies, d.last_post, key=d.id)
        table.loading = False
        if not discussions:
            self.notify("No discussions in this forum", severity="warning")

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
