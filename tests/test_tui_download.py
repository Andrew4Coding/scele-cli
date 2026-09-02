import asyncio
from pathlib import Path

import pytest

pytest.importorskip("textual")

from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from scele import api
from scele.tui.screens.download import DownloadModal


class _ModalTestApp(App):
    CSS_PATH = Path(__file__).resolve().parents[1] / "src/scele/tui/styles/app.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        self.session = object()


def test_download_requires_confirmation_and_reports_progress(tmp_path, monkeypatch):
    asyncio.run(_test_download_requires_confirmation_and_reports_progress(tmp_path, monkeypatch))


async def _test_download_requires_confirmation_and_reports_progress(tmp_path, monkeypatch):
    calls = []

    def fake_download(session, target, out_dir, progress=None):
        calls.append((session, target, out_dir))
        progress(0, 10)
        progress(10, 10)
        return out_dir / "resource.pdf"

    monkeypatch.setattr(api, "download", fake_download)
    app = _ModalTestApp()

    async with app.run_test(size=(100, 30)) as pilot:
        app.push_screen(DownloadModal("https://scele.example/resource", "Slides"))
        await pilot.pause()
        modal = app.screen
        modal.query_one("#download-dir").value = str(tmp_path)
        await pilot.pause()
        assert calls == []

        modal.query_one("#download-submit").press()
        for _ in range(30):
            await pilot.pause(0.05)
            if type(app.screen).__name__ == "Screen":
                break
        assert type(app.screen).__name__ == "Screen"

    assert calls == [(app.session, "https://scele.example/resource", tmp_path)]
