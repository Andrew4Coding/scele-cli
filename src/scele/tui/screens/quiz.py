"""Quiz screens: QuizScreen (settings + attempts), QuizReviewScreen (a finished
attempt), QuizAttemptScreen (answer an in-progress attempt).
"""

from __future__ import annotations

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, DataTable, Footer, Header, Input, Label, Static

from ... import api
from ...session import NotAuthenticatedError


class _StartAttemptModal(ModalScreen[dict | None]):
    """Confirm starting a new quiz attempt (optionally with a password)."""

    BINDINGS = [Binding("escape", "cancel", "Cancel", id="navigation.back")]
    DEFAULT_CSS = """
    _StartAttemptModal { align: center middle; }
    _StartAttemptModal #start-dialog {
        width: 64; height: auto; border: thick $accent; background: $surface; padding: 1 2;
    }
    _StartAttemptModal #start-buttons { align-horizontal: right; height: auto; }
    """

    def __init__(self, cmid: str):
        super().__init__()
        self.cmid = cmid

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="start-dialog"):
            yield Static("[b]Start a new quiz attempt?[/b]\n"
                         "This consumes one of your allowed attempts.")
            yield Label("Quiz password (if required)")
            yield Input(password=True, id="start-password")
            yield Label("", id="start-status")
            with Horizontal(id="start-buttons"):
                yield Button("Cancel", id="start-cancel")
                yield Button("Start", variant="warning", id="start-go")

    @on(Button.Pressed, "#start-cancel")
    def _cancel(self) -> None:
        self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#start-go")
    def _go(self) -> None:
        self.query_one("#start-go", Button).disabled = True
        self.query_one("#start-status", Label).update("Starting…")
        self._start(self.query_one("#start-password", Input).value)

    @work(thread=True)
    def _start(self, password: str) -> None:
        try:
            res = api.quiz_start(self.app.session, self.cmid, password=password)
        except Exception as exc:  # noqa: BLE001
            self.app.call_from_thread(self._fail, str(exc))
        else:
            self.app.call_from_thread(self.dismiss, res)

    def _fail(self, msg: str) -> None:
        self.query_one("#start-go", Button).disabled = False
        self.query_one("#start-status", Label).update(f"[b red]{msg}[/b red]")


class QuizScreen(Screen):
    """One quiz: settings, access rules, and your attempts."""

    BINDINGS = [
        Binding("escape", "go_back", "Back", id="navigation.back"),
        Binding("backspace", "go_back", "Back", show=False),
        Binding("r", "refresh", "Refresh", id="quiz.refresh"),
        Binding("s", "start", "Start attempt", id="quiz.start"),
    ]

    DEFAULT_CSS = """
    QuizScreen #quiz-body { height: 1fr; padding: 0 1; }
    QuizScreen .info-block {
        background: $surface; border: round $panel-lighten-2;
        padding: 1 2; margin-bottom: 1; height: auto;
    }
    QuizScreen #quiz-attempts { height: auto; max-height: 20; }
    """

    def __init__(self, cmid: str):
        super().__init__()
        self.cmid = cmid
        self._attempts: list = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(f"QUIZ · cmid {self.cmid}", id="quiz-title")
        with VerticalScroll(id="quiz-body"):
            yield Static("", id="quiz-summary", classes="info-block")
            yield Static("[b]Your attempts[/b]  [dim](enter = review)[/dim]")
            yield DataTable(id="quiz-attempts")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#quiz-attempts", DataTable)
        table.add_columns("Attempt", "State", "Started", "Finished", "Score")
        table.cursor_type = "row"
        self.query_one("#quiz-body").loading = True
        self._load()

    @work(thread=True)
    def _load(self) -> None:
        try:
            detail = api.quiz(self.app.session, self.cmid)
            self.app.call_from_thread(self._populate, detail)
        except NotAuthenticatedError:
            self.app.call_from_thread(self.notify, "Session expired", severity="error")
        except Exception as exc:  # noqa: BLE001
            self.app.call_from_thread(self.notify, f"Error: {exc}", severity="error")

    def _populate(self, d) -> None:
        self.query_one("#quiz-body").loading = False
        self._detail = d
        self._attempts = d.attempts
        rules = "\n".join(f"  • {r}" for r in d.access_rules) or "  —"
        blocks = "\n".join(f"  • {r}" for r in d.prevented_reasons)
        self.query_one("#quiz-summary", Static).update(
            f"[b]{d.name}[/b]\n"
            f"[cyan]Opens:[/cyan] {d.opens or '—'}   [cyan]Closes:[/cyan] {d.closes or '—'}\n"
            f"[cyan]Time limit:[/cyan] {d.time_limit or 'none'}   "
            f"[cyan]Attempts allowed:[/cyan] {d.attempts_allowed or '∞'}\n"
            f"[cyan]Grade:[/cyan] {d.grade or '—'} ({d.grade_method or '—'})   "
            f"[cyan]Your best:[/cyan] {d.best_grade or '—'}\n"
            f"[cyan]Can attempt now:[/cyan] {'yes' if d.can_attempt else 'no'}\n"
            f"[cyan]Access rules:[/cyan]\n{rules}"
            + (f"\n[red]Blocked:[/red]\n{blocks}" if blocks else "")
        )
        table = self.query_one("#quiz-attempts", DataTable)
        table.clear()
        for a in self._attempts:
            table.add_row(str(a.number), a.state, a.started or "—",
                          a.finished or "—", a.sumgrades or "—", key=a.id)
        if not self._attempts:
            table.add_row("—", "no attempts yet", "", "", "")

    @on(DataTable.RowSelected, "#quiz-attempts")
    def _open_review(self, event: DataTable.RowSelected) -> None:
        if event.row_key.value:
            self.app.push_screen(QuizReviewScreen(str(event.row_key.value)))

    def action_start(self) -> None:
        self.app.push_screen(_StartAttemptModal(self.cmid), self._started)

    def _started(self, res: dict | None) -> None:
        if not res or not res.get("attempt_id"):
            if res and res.get("warnings"):
                self.notify(str(res["warnings"]), severity="error")
            return
        self.notify(f"Attempt {res['attempt_id']} started", severity="information")
        self.app.push_screen(QuizAttemptScreen(res["attempt_id"]), self._attempt_done)

    def _attempt_done(self, _result) -> None:
        self.action_refresh()

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_refresh(self) -> None:
        self.query_one("#quiz-body").loading = True
        self._load()


class QuizReviewScreen(Screen):
    """Per-question review of a finished attempt."""

    BINDINGS = [
        Binding("escape", "go_back", "Back", id="navigation.back"),
        Binding("backspace", "go_back", "Back", show=False),
        Binding("r", "refresh", "Refresh", id="quiz-review.refresh"),
    ]

    DEFAULT_CSS = """
    QuizReviewScreen #review-body { height: 1fr; padding: 0 1; }
    QuizReviewScreen .q-card {
        background: $surface; border: round $panel-lighten-2;
        padding: 1 2; margin-bottom: 1; height: auto;
    }
    """

    def __init__(self, attempt_id: str):
        super().__init__()
        self.attempt_id = attempt_id

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(f"QUIZ REVIEW · attempt {self.attempt_id}", id="review-title")
        yield VerticalScroll(id="review-body")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#review-body").loading = True
        self._load()

    @work(thread=True)
    def _load(self) -> None:
        try:
            review = api.quiz_review(self.app.session, self.attempt_id)
            self.app.call_from_thread(self._populate, review)
        except NotAuthenticatedError:
            self.app.call_from_thread(self.notify, "Session expired", severity="error")
        except Exception as exc:  # noqa: BLE001
            self.app.call_from_thread(self.notify, f"Error: {exc}", severity="error")

    def _populate(self, r) -> None:
        body = self.query_one("#review-body", VerticalScroll)
        body.loading = False
        body.remove_children()
        body.mount(Static(
            f"[b]{r.state}[/b]   grade [b]{r.grade or '—'}[/b]   "
            f"sum {r.sumgrades or '—'}   [dim]{r.started} → {r.finished}[/dim]"
        ))
        for q in r.questions:
            mark = f"{q.mark}/{q.max_mark}" if (q.mark or q.max_mark) else ""
            flag = "  ⚑" if q.flagged else ""
            body.mount(Static(
                f"[b]Q{q.number}. [{q.type}] {q.status} {mark}[/b]{flag}\n{q.text}",
                classes="q-card",
            ))
        if not r.questions:
            body.mount(Static("[dim]No questions in this review[/dim]"))

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_refresh(self) -> None:
        self.query_one("#review-body").loading = True
        self._load()


class QuizAttemptScreen(Screen):
    """Answer an in-progress attempt: one input per question form field."""

    BINDINGS = [
        Binding("escape", "go_back", "Back", id="navigation.back"),
        Binding("ctrl+s", "save", "Save", id="quiz-attempt.save"),
    ]

    DEFAULT_CSS = """
    QuizAttemptScreen #attempt-body { height: 1fr; padding: 0 1; }
    QuizAttemptScreen .q-card {
        background: $surface; border: round $panel-lighten-2;
        padding: 1 2; margin-bottom: 1; height: auto;
    }
    QuizAttemptScreen #attempt-buttons { height: auto; align-horizontal: right; }
    QuizAttemptScreen .answer-input { margin-top: 1; }
    """

    def __init__(self, attempt_id: str, page: int = 0):
        super().__init__()
        self.attempt_id = attempt_id
        self.page = page
        self._inputs: dict[str, Input] = {}

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(f"QUIZ ATTEMPT · {self.attempt_id}", id="attempt-title")
        yield VerticalScroll(id="attempt-body")
        with Horizontal(id="attempt-buttons"):
            yield Button("Save (stay open)", id="attempt-save")
            yield Button("Submit for grading", variant="error", id="attempt-submit")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#attempt-body").loading = True
        self._load()

    @work(thread=True)
    def _load(self) -> None:
        try:
            page = api.quiz_attempt_page(self.app.session, self.attempt_id, self.page)
            self.app.call_from_thread(self._populate, page)
        except NotAuthenticatedError:
            self.app.call_from_thread(self.notify, "Session expired", severity="error")
        except Exception as exc:  # noqa: BLE001
            self.app.call_from_thread(self.notify, f"Error: {exc}", severity="error")

    def _populate(self, page) -> None:
        body = self.query_one("#attempt-body", VerticalScroll)
        body.loading = False
        body.remove_children()
        self._inputs = {}
        body.mount(Static(f"[dim]state: {page.state}   page {page.page}[/dim]"))
        for q in page.questions:
            body.mount(Static(f"[b]Q{q.number}. [{q.type}][/b]\n{q.text}", classes="q-card"))
            for f in q.fields:
                name = f["name"]
                if name.endswith("_:sequencecheck") or name.endswith("_:flagged"):
                    continue
                inp = Input(value=f.get("value", ""), classes="answer-input")
                inp.border_title = name
                self._inputs[name] = inp
                body.mount(inp)
        if not self._inputs:
            body.mount(Static("[dim]No editable fields on this page[/dim]"))

    def _answers(self) -> dict[str, str]:
        return {name: inp.value for name, inp in self._inputs.items()}

    @on(Button.Pressed, "#attempt-save")
    def _save_btn(self) -> None:
        self._submit(finish=False)

    @on(Button.Pressed, "#attempt-submit")
    def _submit_btn(self) -> None:
        self._submit(finish=True)

    def action_save(self) -> None:
        self._submit(finish=False)

    def _submit(self, finish: bool) -> None:
        for b in self.query(Button):
            b.disabled = True
        self.notify("Submitting…" if finish else "Saving…")
        self._send(self._answers(), finish)

    @work(thread=True)
    def _send(self, answers: dict, finish: bool) -> None:
        try:
            res = api.quiz_answer(self.app.session, self.attempt_id, answers,
                                  finish=finish, page=self.page)
        except Exception as exc:  # noqa: BLE001
            self.app.call_from_thread(self._after, {"error": str(exc)})
        else:
            self.app.call_from_thread(self._after, res)

    def _after(self, res: dict) -> None:
        for b in self.query(Button):
            b.disabled = False
        if res.get("error"):
            self.notify(res["error"], severity="error")
            return
        if res.get("warnings"):
            self.notify(str(res["warnings"]), severity="warning")
        if res.get("finished"):
            self.notify("Submitted for grading.", severity="information")
            self.app.pop_screen()
        else:
            self.notify(f"Saved (state: {res.get('state', '?')}).", severity="information")

    def action_go_back(self) -> None:
        self.app.pop_screen()
