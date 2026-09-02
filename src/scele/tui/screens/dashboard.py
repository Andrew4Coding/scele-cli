from __future__ import annotations

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Static

from ... import api
from ...models import Announcement, Course
from ...session import NotAuthenticatedError
from ..widgets.search import FIND_BINDING, SearchableScreen, SearchBar


class DashboardScreen(SearchableScreen, Screen[None]):
    """Main dashboard showing courses and announcements."""

    BINDINGS = [
        Binding("r", "refresh", "Refresh", id="dashboard.refresh"),
        Binding("a", "announcements", "Announcements", id="dashboard.announcements"),
        Binding("escape", "go_back", "Back", id="navigation.back"),
        FIND_BINDING,
    ]

    search_focus = "#courses-table"

    DEFAULT_CSS = """
    #dashboard-layout {
        height: 1fr;
    }
    #courses-panel {
        width: 70%;
        height: 1fr;
        padding: 0 1;
    }
    #announcements-panel {
        width: 30%;
        height: 1fr;
        padding: 0 1;
        border-left: solid $accent;
    }
    #courses-title, #announcements-title {
        text-style: bold;
        padding: 1 0;
        color: $accent;
    }
    #courses-table {
        height: 1fr;
    }
    #announcements-list {
        height: 1fr;
    }
    .announcement-card {
        padding: 1;
        border: round $primary;
        margin-bottom: 1;
        background: $surface;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="dashboard-layout"):
            with Vertical(id="courses-panel"):
                yield Static("MY COURSES", id="courses-title")
                yield SearchBar()
                yield DataTable(id="courses-table")
            with Vertical(id="announcements-panel"):
                yield Static("ANNOUNCEMENTS", id="announcements-title")
                yield VerticalScroll(id="announcements-list")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#courses-table", DataTable)
        table.add_columns("ID", "Name", "Category")
        table.cursor_type = "row"
        table.loading = True
        self._courses: list[Course] = []
        self._load_data()

    @work(thread=True)
    def _load_data(self) -> None:
        try:
            session = self.app.session
            courses = api.my_courses(session)
            announcements = api.announcements(session)
            self.app.call_from_thread(self._populate, courses, announcements)
        except NotAuthenticatedError:
            self.app.call_from_thread(
                self.notify, "Session expired. Please login again.", severity="error"
            )
        except Exception as e:
            self.app.call_from_thread(self.notify, f"Error: {e}", severity="error")

    def _populate(self, courses: list[Course], announcements: list[Announcement]) -> None:
        self._courses = courses
        self._render_courses()
        self.query_one("#courses-table", DataTable).loading = False

        ann_list = self.query_one("#announcements-list", VerticalScroll)
        ann_list.remove_children()
        ann_list.loading = False
        for a in announcements[:5]:  # Show latest 5
            body_preview = a.body[:150] + ("..." if len(a.body) > 150 else "")
            ann_list.mount(
                Static(
                    f"[b]{a.subject}[/b]\n"
                    f"[dim]{a.author} — {a.date}[/dim]\n"
                    f"{body_preview}",
                    classes="announcement-card",
                )
            )
        if not announcements:
            ann_list.mount(Static("[dim]No announcements[/dim]"))

    def _render_courses(self) -> None:
        """Fill the courses table with rows that match the active filter."""
        table = self.query_one("#courses-table", DataTable)
        table.clear()
        query = self.search_query
        for c in self._courses:
            if query and query not in f"{c.id} {c.name} {c.category}".lower():
                continue
            table.add_row(c.id, c.name, c.category, key=c.id)

    def filter_list(self, query: str) -> None:
        self._render_courses()

    @on(DataTable.RowSelected, "#courses-table")
    def on_course_selected(self, event: DataTable.RowSelected) -> None:
        row_key = event.row_key
        course_id = str(row_key.value)
        try:
            from .course import CourseScreen

            self.app.push_screen(CourseScreen(course_id))
        except ImportError:
            self.notify(f"Course {course_id} selected", severity="information")

    def action_refresh(self) -> None:
        table = self.query_one("#courses-table", DataTable)
        table.clear()
        table.loading = True
        ann_list = self.query_one("#announcements-list", VerticalScroll)
        ann_list.remove_children()
        ann_list.loading = True
        self._load_data()

    def action_announcements(self) -> None:
        try:
            from .announcements import AnnouncementsScreen

            self.app.push_screen(AnnouncementsScreen())
        except ImportError:
            self.notify("Announcements screen not implemented yet", severity="information")

    def action_go_back(self) -> None:
        self.app.pop_screen()
