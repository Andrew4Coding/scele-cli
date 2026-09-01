from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

from ..config import CONFIG_DIR


SETTINGS_PATH = CONFIG_DIR / "tui.json"
DEFAULT_THEME = "scele-dark"

DEFAULT_KEYMAP = {
    "app.quit": "q",
    "app.toggle_dark": "d",
    "app.help": "question_mark",
    "app.settings": "f2",
    "navigation.back": "escape",
    "dashboard.refresh": "r",
    "dashboard.announcements": "a",
    "course.refresh": "r",
    "forum.refresh": "r",
    "forum.new_discussion": "n",
    "thread.refresh": "r",
    "thread.reply": "n",
    "assignment.refresh": "r",
    "announcements.refresh": "r",
}

KEYBINDING_LABELS = (
    ("app.quit", "Quit application"),
    ("app.toggle_dark", "Toggle light/dark theme"),
    ("app.help", "Show help"),
    ("app.settings", "Open settings"),
    ("navigation.back", "Back / cancel"),
    ("dashboard.refresh", "Refresh dashboard"),
    ("dashboard.announcements", "Open announcements"),
    ("course.refresh", "Refresh course"),
    ("forum.refresh", "Refresh forum"),
    ("forum.new_discussion", "New discussion"),
    ("thread.refresh", "Refresh thread"),
    ("thread.reply", "Reply to post"),
    ("assignment.refresh", "Refresh assignment"),
    ("announcements.refresh", "Refresh announcements"),
)

_KEY_RE = re.compile(
    r"^(?:(?:ctrl|shift|alt|meta|super)\+)*[a-z0-9_?.,-]+$"
)


def normalize_key(value: str) -> str:
    """Return the Textual key name for a user-entered shortcut."""
    value = value.strip().lower()
    return "question_mark" if value == "?" else value


def is_valid_key(value: str) -> bool:
    """Check the single-key format accepted by the settings editor."""
    value = normalize_key(value)
    return bool(value and "," not in value and _KEY_RE.fullmatch(value))


def key_for_display(value: str) -> str:
    """Use the familiar punctuation form for keys in the settings editor."""
    return "?" if value == "question_mark" else value


@dataclass
class TuiSettings:
    """Persisted preferences that do not contain credentials or session data."""

    theme: str = DEFAULT_THEME
    keymap: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_KEYMAP))

    def __post_init__(self) -> None:
        configured = self.keymap if isinstance(self.keymap, dict) else {}
        merged = dict(DEFAULT_KEYMAP)
        for action in DEFAULT_KEYMAP:
            value = configured.get(action)
            if isinstance(value, str) and is_valid_key(value):
                merged[action] = normalize_key(value)
        self.keymap = merged

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def default_settings() -> TuiSettings:
    return TuiSettings()


def load_settings(path: Path | None = None) -> TuiSettings:
    """Load UI preferences, falling back safely on missing or malformed JSON."""
    settings_path = Path(path) if path is not None else SETTINGS_PATH
    if not settings_path.exists():
        return default_settings()
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default_settings()
    if not isinstance(data, dict):
        return default_settings()
    theme = data.get("theme", DEFAULT_THEME)
    keymap = data.get("keymap", {})
    return TuiSettings(
        theme=theme if isinstance(theme, str) and theme else DEFAULT_THEME,
        keymap=keymap if isinstance(keymap, dict) else {},
    )


def save_settings(settings: TuiSettings, path: Path | None = None) -> None:
    """Persist UI preferences without touching the credential cookie store."""
    settings_path = Path(path) if path is not None else SETTINGS_PATH
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(
        json.dumps(settings.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )
    try:
        settings_path.chmod(0o600)
    except (OSError, NotImplementedError):
        pass
