"""TableScreen — a screen that loads one api call in a worker thread and shows
the result in a DataTable. Cuts the boilerplate shared by the list screens
(deadlines, calendar, notifications, grades, people).
"""

from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Static

from ...session import NotAuthenticatedError
from .search import FIND_BINDING, SearchableScreen, SearchBar


class TableScreen(SearchableScreen, Screen):
    """Base list screen. Subclasses set ``heading`` / ``columns`` and implement
    ``fetch(session)`` and ``to_row(item)``; optionally ``row_selected(key)``.
    """

    heading = "DATA"
    columns: tuple[str, ...] = ()
    row_key_index: int | None = None
    empty_message = "Nothing to show"

    BINDINGS = [
        Binding("escape", "go_back", "Back", id="navigation.back"),
        Binding("backspace", "go_back", "Back", show=False),
        Binding("r", "refresh", "Refresh", id="table.refresh"),
        FIND_BINDING,
    ]

    search_focus = "#data-table"

    DEFAULT_CSS = """
    TableScreen #table-heading {
        text-style: bold;
        color: $accent;
        padding: 1 0 0 1;
    }
    TableScreen #data-table {
        height: 1fr;
    }
    """

    # -- to override -------------------------------------------------------

    def fetch(self, session):  # pragma: no cover - overridden
        raise NotImplementedError

    def to_row(self, item) -> tuple:  # pragma: no cover - overridden
        raise NotImplementedError

    def row_selected(self, key: str | None) -> None:
        """Called when a row is activated; ``key`` is the row_key_index cell."""

    @property
    def current_item(self):
        """The data object under the table cursor (filter-aware), or None."""
        try:
            row = self.query_one("#data-table", DataTable).cursor_row
        except Exception:
            return None
        return self._rows[row] if row is not None and 0 <= row < len(self._rows) else None

    # -- plumbing --------------------------------------------------------

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(self.heading, id="table-heading")
        yield SearchBar()
        yield DataTable(id="data-table")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#data-table", DataTable)
        table.add_columns(*self.columns)
        table.cursor_type = "row"
        table.loading = True
        self._items: list = []
        self._rows: list = []
        self._load()

    @work(thread=True)
    def _load(self) -> None:
        try:
            items = self.fetch(self.app.session)
            self.app.call_from_thread(self._populate, list(items))
        except NotAuthenticatedError:
            self.app.call_from_thread(self.notify, "Session expired", severity="error")
        except Exception as exc:  # noqa: BLE001 - surface any failure in the UI
            self.app.call_from_thread(self.notify, f"Error: {exc}", severity="error")
            self.app.call_from_thread(self._stop_loading)

    def _stop_loading(self) -> None:
        self.query_one("#data-table", DataTable).loading = False

    def _populate(self, items: list) -> None:
        self._items = items
        self._render_rows()
        self.query_one("#data-table", DataTable).loading = False
        if not items:
            self.notify(self.empty_message, severity="information")

    def _render_rows(self) -> None:
        table = self.query_one("#data-table", DataTable)
        table.clear()
        query = self.search_query
        self._rows: list = []
        for item in self._items:
            row = tuple("" if c is None else str(c) for c in self.to_row(item))
            if query and query not in " ".join(row).lower():
                continue
            key = row[self.row_key_index] if self.row_key_index is not None else None
            table.add_row(*row, key=key)
            self._rows.append(item)

    def filter_list(self, query: str) -> None:
        self._render_rows()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        value = event.row_key.value
        self.row_selected(str(value) if value is not None else None)

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_refresh(self) -> None:
        self.query_one("#data-table", DataTable).loading = True
        self._load()
