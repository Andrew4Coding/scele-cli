import json
from pathlib import Path

import pytest

pytest.importorskip("textual")

from scele.tui.app import SceleApp
from scele.tui.settings import (
    DEFAULT_KEYMAP,
    TuiSettings,
    load_settings,
    save_settings,
)


def test_settings_round_trip_isolated_from_cookies(tmp_path: Path):
    path = tmp_path / "tui.json"
    settings = TuiSettings(
        theme="scele-light",
        keymap={"app.quit": "ctrl+x", "app.help": "?"},
    )

    save_settings(settings, path)
    loaded = load_settings(path)

    assert loaded.theme == "scele-light"
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
