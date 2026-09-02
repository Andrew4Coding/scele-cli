import asyncio
from pathlib import Path

import pytest

pytest.importorskip("textual")

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from scele import api
from scele.tui.screens.composer import NewDiscussionModal, ReplyModal


class _ModalTestApp(App):
    CSS_PATH = Path(__file__).resolve().parents[1] / "src/scele/tui/styles/app.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        self.session = object()


async def _wait_for_worker(pilot, app) -> None:
    for _ in range(30):
        await pilot.pause(0.05)
        if type(app.screen).__name__ == "Screen":
            return
    raise AssertionError(f"modal did not finish, got {type(app.screen).__name__}")


def test_new_discussion_requires_submit_and_posts(monkeypatch):
    asyncio.run(_test_new_discussion_requires_submit_and_posts(monkeypatch))


async def _test_new_discussion_requires_submit_and_posts(monkeypatch):
    calls = []

    def fake_post(session, forum_id, subject, message):
        calls.append((session, forum_id, subject, message))
        return "https://scele.example/thread/1"

    monkeypatch.setattr(api, "forum_post", fake_post)
    app = _ModalTestApp()

    async with app.run_test(size=(100, 30)) as pilot:
        app.push_screen(NewDiscussionModal("42"))
        await pilot.pause()
        modal = app.screen
        modal.query_one("#composer-subject").value = "A subject"
        modal.query_one("#composer-message").text = "A message"
        await pilot.pause()
        assert calls == []

        modal.query_one("#composer-submit").press()
        await _wait_for_worker(pilot, app)

    assert calls == [(app.session, "42", "A subject", "A message")]


def test_reply_posts_to_selected_post(monkeypatch):
    asyncio.run(_test_reply_posts_to_selected_post(monkeypatch))


async def _test_reply_posts_to_selected_post(monkeypatch):
    calls = []

    def fake_reply(session, post_id, message):
        calls.append((session, post_id, message))
        return "https://scele.example/thread/2"

    monkeypatch.setattr(api, "forum_reply", fake_reply)
    app = _ModalTestApp()

    async with app.run_test(size=(100, 30)) as pilot:
        app.push_screen(ReplyModal("post-7"))
        await pilot.pause()
        modal = app.screen
        modal.query_one("#composer-message").text = "A reply"
        modal.query_one("#composer-submit").press()
        await _wait_for_worker(pilot, app)

    assert calls == [(app.session, "post-7", "A reply")]
