"""CourseInfoScreen — course-detail (category, dates, teachers, summary) plus
course-updates (what changed recently).
"""

from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from ... import api
from ...session import NotAuthenticatedError


class CourseInfoScreen(Screen):
    """Metadata + recent activity for one course."""

    BINDINGS = [
        Binding("escape", "go_back", "Back", id="navigation.back"),
        Binding("backspace", "go_back", "Back", show=False),
        Binding("r", "refresh", "Refresh", id="course-info.refresh"),
    ]

    DEFAULT_CSS = """
    CourseInfoScreen #course-info-body { height: 1fr; padding: 0 1; }
    CourseInfoScreen .info-block {
        background: $surface;
        border: round $panel-lighten-2;
        padding: 1 2;
        margin-bottom: 1;
        height: auto;
    }
    """

    def __init__(self, course_id: str):
        super().__init__()
        self.course_id = course_id

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(f"COURSE INFO · {self.course_id}", id="course-info-title")
        yield VerticalScroll(id="course-info-body")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#course-info-body").loading = True
        self._load()

    @work(thread=True)
    def _load(self) -> None:
        try:
            session = self.app.session
            detail = api.course_detail(session, self.course_id)
            try:
                updates = api.course_updates(session, self.course_id, since_days=14)
            except Exception:  # noqa: BLE001 - updates are best-effort
                updates = {"updated": []}
            self.app.call_from_thread(self._populate, detail, updates)
        except NotAuthenticatedError:
            self.app.call_from_thread(self.notify, "Session expired", severity="error")
        except Exception as exc:  # noqa: BLE001
            self.app.call_from_thread(self.notify, f"Error: {exc}", severity="error")

    def _populate(self, d, updates) -> None:
        body = self.query_one("#course-info-body", VerticalScroll)
        body.loading = False
        body.remove_children()

        teachers = "\n".join(f"  • {t.get('name', '')}" for t in d.teachers) \
            or "  (none listed)"
        body.mount(Static(
            f"[b]{d.fullname}[/b]  [dim]{d.shortname}[/dim]\n"
            f"[cyan]Category:[/cyan] {d.category or '—'}\n"
            f"[cyan]Runs:[/cyan] {d.start or '?'} → {d.end or '?'}\n"
            f"[cyan]Teachers:[/cyan]\n{teachers}"
            + (f"\n\n{d.summary}" if d.summary else ""),
            classes="info-block",
        ))

        rows = updates.get("updated") or []
        if rows:
            lines = "\n".join(
                f"  • cmid {r.get('cmid')}: {', '.join(r.get('changed') or []) or '—'}"
                for r in rows
            )
            body.mount(Static(f"[b]Changed in the last 14 days[/b]\n{lines}",
                              classes="info-block"))
        else:
            body.mount(Static("[dim]No recent changes[/dim]", classes="info-block"))

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_refresh(self) -> None:
        self.query_one("#course-info-body").loading = True
        self._load()
