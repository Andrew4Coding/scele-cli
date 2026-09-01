from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Static

from ... import api
from ...session import NotAuthenticatedError


class AssignmentScreen(Screen):
    """Assignment detail view showing submission status."""

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("backspace", "go_back", "Back", show=False),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self, cmid: str):
        super().__init__()
        self.cmid = cmid

    def compose(self) -> ComposeResult:
        yield Header()
        yield VerticalScroll(
            Static(f"📋 Assignment {self.cmid}", id="assignment-title"),
            Static("", id="assignment-name"),
            Static("─" * 50, classes="separator"),
            Vertical(id="assignment-fields"),
            Static("", id="files-header"),
            DataTable(id="files-table"),
            id="assignment-content",
        )
        yield Footer()

    def on_mount(self) -> None:
        files_table = self.query_one("#files-table", DataTable)
        files_table.add_columns("Name", "URL")
        files_table.cursor_type = "row"
        self.loading = True
        self._load_assignment()

    @work(thread=True)
    def _load_assignment(self) -> None:
        try:
            session = self.app.session
            status = api.assignment(session, self.cmid)
            self.app.call_from_thread(self._populate, status)
        except NotAuthenticatedError:
            self.app.call_from_thread(self.notify, "Session expired", severity="error")
        except Exception as e:
            self.app.call_from_thread(self.notify, f"Error: {e}", severity="error")

    def _populate(self, status) -> None:
        self.loading = False
        self.query_one("#assignment-name", Static).update(
            f"[b]{status.name or 'Assignment'}[/b]\n[dim]cmid: {status.cmid}[/dim]"
        )

        # Populate fields as key-value pairs
        fields_container = self.query_one("#assignment-fields", Vertical)
        fields_container.remove_children()
        if status.fields:
            for key, value in status.fields.items():
                fields_container.mount(
                    Static(f"[cyan]{key}:[/cyan]  {value}", classes="field-row")
                )
        else:
            fields_container.mount(Static("[dim]No status fields[/dim]"))

        # Populate files table
        if status.files:
            self.query_one("#files-header", Static).update("[b]📎 Attached Files[/b]")
            table = self.query_one("#files-table", DataTable)
            table.clear()
            table.display = True
            for f in status.files:
                table.add_row(
                    f.get("name", "unknown"),
                    f.get("url", "—"),
                )
        else:
            self.query_one("#files-header", Static).update("[dim]No attached files[/dim]")
            self.query_one("#files-table", DataTable).display = False

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_refresh(self) -> None:
        self.loading = True
        self._load_assignment()
