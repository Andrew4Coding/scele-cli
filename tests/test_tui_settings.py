import asyncio
import json
from pathlib import Path

import pytest

pytest.importorskip("textual")

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, DataTable, Input, Select

from scele.tui.app import SceleApp
from scele.tui.screens.settings import SettingsScreen
from scele.tui.settings import (
    DEFAULT_KEYMAP,
    TuiSettings,
    load_settings,
    save_settings,
)


class _VimTestApp(SceleApp):
    CSS_PATH = Path(__file__).resolve().parents[1] / "src/scele/tui/styles/app.tcss"

    def _check_auth(self) -> None:
        pass


class _TableScreen(Screen):
    def compose(self) -> ComposeResult:
        yield DataTable(id="table")

    def on_mount(self) -> None:
        table = self.query_one("#table", DataTable)
        table.add_column("Value")
        table.add_row("one")
        table.add_row("two")
        table.focus()


class _InputScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Input(id="input")

    def on_mount(self) -> None:
        self.query_one("#input", Input).focus()


def test_settings_round_trip_isolated_from_cookies(tmp_path: Path):
    path = tmp_path / "tui.json"
    settings = TuiSettings(
        theme="scele-light",
        keybinding_mode="vim",
        keymap={"app.quit": "ctrl+x", "app.help": "?"},
    )

    save_settings(settings, path)
    loaded = load_settings(path)

    assert loaded.theme == "scele-light"
    assert loaded.keybinding_mode == "vim"
    assert loaded.keymap["app.quit"] == "ctrl+x"
    assert loaded.keymap["app.help"] == "question_mark"
    assert loaded.keymap["navigation.back"] == DEFAULT_KEYMAP["navigation.back"]
    assert json.loads(path.read_text(encoding="utf-8"))["theme"] == "scele-light"
    assert not (tmp_path / "cookies.json").exists()


def test_scele_app_applies_saved_theme_and_keymap(tmp_path, monkeypatch):
    path = tmp_path / "tui.json"
    save_settings(TuiSettings(theme="scele-light", keymap={"app.quit": "ctrl+x"}), path)

    import scele.tui.settings as tui_settings

    monkeypatch.setattr(tui_settings, "SETTINGS_PATH", path)
    app = SceleApp()

    assert app.theme == "scele-light"
    assert app.settings.keymap["app.quit"] == "ctrl+x"


def test_vim_actions_are_gated_by_mode():
    app = SceleApp()

    app.settings.keybinding_mode = "default"
    assert app.check_action("vim_down", ()) is False

    app.settings.keybinding_mode = "vim"
    assert app.check_action("vim_down", ()) is True


def test_vim_navigation_moves_widgets_without_stealing_text_input():
    asyncio.run(_test_vim_navigation_moves_widgets_without_stealing_text_input())


async def _test_vim_navigation_moves_widgets_without_stealing_text_input():
    app = _VimTestApp()
    app.settings.keybinding_mode = "vim"

    async with app.run_test(size=(100, 30)) as pilot:
        app.push_screen(_TableScreen())
        await pilot.pause()
        table = app.screen.query_one("#table", DataTable)
        assert table.cursor_row == 0
        await pilot.press("j")
        await pilot.pause()
        assert table.cursor_row == 1
        await pilot.press("k")
        await pilot.pause()
        assert table.cursor_row == 0

        app.push_screen(_InputScreen())
        await pilot.pause()
        await pilot.press("j")
        await pilot.pause()
        assert app.screen.query_one("#input", Input).value == "j"


def test_settings_screen_applies_vim_mode(tmp_path, monkeypatch):
    import scele.tui.settings as tui_settings

    settings_path = tmp_path / "tui.json"
    monkeypatch.setattr(tui_settings, "SETTINGS_PATH", settings_path)
    asyncio.run(_test_settings_screen_applies_vim_mode(settings_path))


async def _test_settings_screen_applies_vim_mode(settings_path: Path):
    app = _VimTestApp()

    async with app.run_test(size=(100, 40)) as pilot:
        app.push_screen(SettingsScreen())
        await pilot.pause()
        app.screen.query_one("#settings-mode", Select).value = "vim"
        app.screen.query_one("#settings-save", Button).press()
        for _ in range(20):
            await pilot.pause(0.05)
            if type(app.screen).__name__ == "Screen":
                break
        assert type(app.screen).__name__ == "Screen"

    assert app.settings.keybinding_mode == "vim"
    assert load_settings(settings_path).keybinding_mode == "vim"
