"""Smoke tests for the screens that surface the newer CLI commands."""

import asyncio
from pathlib import Path

import pytest

pytest.importorskip("textual")

from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import DataTable, Footer, Header

from scele import api
from scele.models import (
    AssignmentInfo, Deadline, Grade, Notification, Person, QuizAttempt, QuizDetail,
    QuizQuestion, QuizReview,
)
from scele.tui.screens.course_info import CourseInfoScreen
from scele.tui.screens.lists import (
    DeadlinesScreen, GradesScreen, NotificationsScreen, PeopleScreen,
)
from scele.tui.screens.quiz import QuizReviewScreen, QuizScreen
from scele.tui.screens.submit import AssignmentDetailScreen


class _App(App):
    CSS_PATH = Path(__file__).resolve().parents[1] / "src/scele/tui/styles/app.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        self.session = object()


async def _settle(pilot, check):
    for _ in range(40):
        await pilot.pause(0.05)
        if check():
            return
    raise AssertionError("screen never settled")


def _run(coro):
    asyncio.run(coro)


def test_deadlines_screen_lists_rows(monkeypatch):
    monkeypatch.setattr(api, "deadlines", lambda s, days=30: [
        Deadline(name="HW1 due", course="DDP2", course_id="2", when="2026-09-10 10:00 WIB",
                 due_in="in 3d", type="Assignment"),
    ])

    async def go():
        app = _App()
        async with app.run_test(size=(120, 30)) as pilot:
            app.push_screen(DeadlinesScreen())
            table = lambda: app.screen.query_one("#data-table", DataTable)
            await _settle(pilot, lambda: not table().loading)
            assert table().row_count == 1

    _run(go())


def test_grades_and_people_and_notifications_screens(monkeypatch):
    monkeypatch.setattr(api, "grades", lambda s, cid: [
        Grade(item="Quiz 1", grade="88", range="0–100", percentage="88 %")])
    monkeypatch.setattr(api, "people", lambda s, cid: [
        Person(id="1", name="Dr Yugo", roles=["editingteacher"], email="y@x")])
    monkeypatch.setattr(api, "notifications", lambda s, limit=40: [
        Notification(id="1", subject="Graded", sender="mod_assign", time="t", text="done")])

    async def go():
        app = _App()
        async with app.run_test(size=(120, 30)) as pilot:
            for screen in (GradesScreen("4234"), PeopleScreen("4234"), NotificationsScreen()):
                app.push_screen(screen)
                table = lambda: app.screen.query_one("#data-table", DataTable)
                await _settle(pilot, lambda: not table().loading)
                assert table().row_count == 1
                app.pop_screen()
                await pilot.pause()

    _run(go())


def test_course_info_screen(monkeypatch):
    from scele.models import CourseDetail

    monkeypatch.setattr(api, "course_detail", lambda s, cid: CourseDetail(
        id="4234", shortname="Komas", fullname="Komputer & Masyarakat",
        category="REG", start="2026", end="2027",
        teachers=[{"id": "1", "name": "Dr Yugo"}]))
    monkeypatch.setattr(api, "course_updates", lambda s, cid, since_days=14: {
        "updated": [{"cmid": 1, "changed": ["submissions"]}]})

    async def go():
        app = _App()
        async with app.run_test(size=(120, 30)) as pilot:
            app.push_screen(CourseInfoScreen("4234"))
            body = lambda: app.screen.query_one("#course-info-body", VerticalScroll)
            await _settle(pilot, lambda: not body().loading)
            assert len(body().children) == 2

    _run(go())


def test_quiz_screen_and_review(monkeypatch):
    monkeypatch.setattr(api, "quiz", lambda s, cmid: QuizDetail(
        cmid=cmid, id="8228", name="Mini quiz", time_limit="10 mins",
        attempts_allowed=1, grade="10", best_grade="10", can_attempt=False,
        access_rules=["Attempts allowed: 1"], prevented_reasons=["not available"],
        attempts=[QuizAttempt(id="459484", number=1, state="finished", sumgrades="10")]))
    monkeypatch.setattr(api, "quiz_review", lambda s, aid: QuizReview(
        attempt_id=aid, quiz_id="8228", state="finished", grade="10",
        questions=[QuizQuestion(number=1, slot=1, type="numerical", status="Correct",
                                mark="10.00", max_mark="10", text="Q text")]))

    async def go():
        app = _App()
        async with app.run_test(size=(120, 30)) as pilot:
            app.push_screen(QuizScreen("188689"))
            table = lambda: app.screen.query_one("#quiz-attempts", DataTable)
            await _settle(pilot, lambda: not app.screen.query_one("#quiz-body").loading)
            assert table().row_count == 1

            app.push_screen(QuizReviewScreen("459484"))
            body = lambda: app.screen.query_one("#review-body", VerticalScroll)
            await _settle(pilot, lambda: not body().loading)
            # header line + one question card
            assert len(body().children) == 2

    _run(go())


def test_assignment_detail_screen(monkeypatch):
    monkeypatch.setattr(api, "assignment_detail", lambda s, ref: AssignmentInfo(
        id="900", cmid="55010", course_id="4234", name="HW1", due="2026-09-01 10:00 WIB",
        due_in="overdue 2d", instructions="Do the thing",
        attachments=[{"filename": "brief.pdf", "filesize": 1234, "fileurl": "https://x"}]))

    async def go():
        app = _App()
        async with app.run_test(size=(120, 30)) as pilot:
            app.push_screen(AssignmentDetailScreen("55010"))
            table = lambda: app.screen.query_one("#detail-files", DataTable)
            await _settle(pilot, lambda: not app.screen.query_one("#detail-body").loading)
            assert table().row_count == 1

    _run(go())
