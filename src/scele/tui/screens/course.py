from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, Header, Static, Tree

from ... import api
from ...models import Activity
from ...session import NotAuthenticatedError
from ..widgets.search import FIND_BINDING, SearchableScreen, SearchBar

# Type icons for activities
TYPE_ICONS = {
    "forum": "◇",
    "assign": "▤",
    "resource": "▦",
    "folder": "▸",
    "url": "↗",
    "page": "≡",
    "label": "•",
}


class CourseScreen(SearchableScreen, Screen):
    """Course outline showing sections and activities."""

    BINDINGS = [
        Binding("escape", "go_back", "Back", id="navigation.back"),
        Binding("backspace", "go_back", "Back", show=False),
        Binding("r", "refresh", "Refresh", id="course.refresh"),
        Binding("i", "info", "Info", id="course.info"),
        Binding("g", "grades", "Grades", id="course.grades"),
        Binding("p", "people", "People", id="course.people"),
        FIND_BINDING,
    ]

    search_focus = "#course-tree"

    def __init__(self, course_id: str):
        super().__init__()
        self.course_id = course_id
        self._sections = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(f"COURSE {self.course_id}", id="course-title")
        yield SearchBar()
        yield Tree("Sections", id="course-tree")
        yield Footer()

    def on_mount(self) -> None:
        tree = self.query_one("#course-tree", Tree)
        tree.root.expand()
        tree.loading = True
        self._load_course()

    @work(thread=True)
    def _load_course(self) -> None:
        try:
            session = self.app.session
            sections = api.course(session, self.course_id)
            self.app.call_from_thread(self._populate_tree, sections)
        except NotAuthenticatedError:
            self.app.call_from_thread(self.notify, "Session expired", severity="error")
        except Exception as e:
            self.app.call_from_thread(self.notify, f"Error: {e}", severity="error")

    def _populate_tree(self, sections) -> None:
        self._sections = sections
        self._render_tree()
        self.query_one("#course-tree", Tree).loading = False

    def _render_tree(self) -> None:
        """Rebuild the tree, keeping only sections/activities that match the filter."""
        tree = self.query_one("#course-tree", Tree)
        tree.clear()
        query = self.search_query
        for sec in self._sections:
            section_hit = not query or query in (sec.name or "").lower()
            matched = [
                act
                for act in sec.activities
                if query in f"{act.type} {act.name}".lower()
            ]
            if query and not section_hit and not matched:
                continue
            activities = sec.activities if section_hit else matched
            section_label = f"▸ {sec.name}" if sec.name else "▸ (unnamed section)"
            section_node = tree.root.add(section_label, expand=True)
            if sec.summary and not query:
                section_node.add_leaf(f"[dim]{sec.summary[:100]}[/dim]")
            for act in activities:
                icon = TYPE_ICONS.get(act.type, "·")
                label = f"{icon} [{act.type}] {act.name}"
                section_node.add_leaf(label, data=act)

    def filter_list(self, query: str) -> None:
        self._render_tree()

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle selection of a tree node (activity)."""
        node = event.node
        if node.data is None:
            return
        activity = node.data
        if not isinstance(activity, Activity):
            return

        if activity.type == "forum":
            from .forum import ForumScreen

            self.app.push_screen(ForumScreen(activity.cmid))
        elif activity.type == "assign":
            from .assignment import AssignmentScreen

            self.app.push_screen(AssignmentScreen(activity.cmid))
        elif activity.type in ("resource", "folder"):
            from .download import DownloadModal

            self.app.push_screen(
                DownloadModal(activity.url, activity.name),
                self._download_finished,
            )
        else:
            self.notify(f"Opening {activity.type}: {activity.name}", title="Activity")

    def _download_finished(self, result: dict[str, object] | None) -> None:
        if not result or not result.get("ok"):
            return
        self.notify(f"Downloaded to {result.get('path', 'disk')}", severity="information")

    def action_info(self) -> None:
        from .course_info import CourseInfoScreen

        self.app.push_screen(CourseInfoScreen(self.course_id))

    def action_grades(self) -> None:
        from .lists import GradesScreen

        self.app.push_screen(GradesScreen(self.course_id))

    def action_people(self) -> None:
        from .lists import PeopleScreen

        self.app.push_screen(PeopleScreen(self.course_id))

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_refresh(self) -> None:
        tree = self.query_one("#course-tree", Tree)
        tree.clear()
        tree.loading = True
        self._load_course()
