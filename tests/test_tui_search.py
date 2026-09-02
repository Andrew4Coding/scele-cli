import asyncio
from pathlib import Path

import pytest

pytest.importorskip("textual")

from textual.app import App, ComposeResult
from textual.widgets import DataTable, Footer, Header

from scele import api
from scele.models import Announcement, Discussion
from scele.tui.screens.announcements import AnnouncementsScreen
from scele.tui.screens.forum import ForumScreen
from scele.tui.widgets.search import SearchBar
from textual.containers import VerticalScroll


class _TestApp(App):
    CSS_PATH = Path(__file__).resolve().parents[1] / "src/scele/tui/styles/app.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        self.session = object()


DISCUSSIONS = [
    Discussion(id="1", name="Assignment 1 released", url="", author="Alice", replies=2),
    Discussion(id="2", name="Midterm logistics", url="", author="Bob", replies=0),
    Discussion(id="3", name="Assignment 2 hints", url="", author="Alice", replies=5),
]


def test_find_key_filters_forum_rows(monkeypatch):
    asyncio.run(_run(monkeypatch))


async def _run(monkeypatch):
    monkeypatch.setattr(api, "forum", lambda session, forum_id: list(DISCUSSIONS))
    app = _TestApp()

    async with app.run_test(size=(100, 30)) as pilot:
        app.push_screen(ForumScreen("42"))
        for _ in range(30):
            await pilot.pause(0.05)
            if not app.screen.query_one("#forum-table", DataTable).loading:
                break
        table = app.screen.query_one("#forum-table", DataTable)
        assert table.row_count == 3

        await pilot.press("f")
        await pilot.pause()
        bar = app.screen.query_one(SearchBar)
        assert bar.has_class("-active")

        for ch in "assignment":
            await pilot.press(ch)
        await pilot.pause()
        assert table.row_count == 2

        await pilot.press("escape")
        await pilot.pause()
        assert not bar.has_class("-active")
        assert table.row_count == 3


def test_find_key_filters_announcement_cards(monkeypatch):
    asyncio.run(_run_announcements(monkeypatch))


async def _run_announcements(monkeypatch):
    monkeypatch.setattr(
        api,
        "announcements",
        lambda session: [
            Announcement(subject="Campus closed", author="Admin", date="d", body="holiday"),
            Announcement(subject="Grades posted", author="Lecturer", date="d", body="check portal"),
        ],
    )
    app = _TestApp()

    async with app.run_test(size=(100, 30)) as pilot:
        app.push_screen(AnnouncementsScreen())
        for _ in range(30):
            await pilot.pause(0.05)
            if not app.screen.query_one("#announcements-list", VerticalScroll).loading:
                break
        cards = app.screen.query_one("#announcements-list", VerticalScroll)
        assert len(cards.children) == 2

        await pilot.press("f")
        for ch in "grades":
            await pilot.press(ch)
        await pilot.pause()
        assert len(cards.children) == 1

        await pilot.press("escape")
        await pilot.pause()
        assert len(cards.children) == 2
