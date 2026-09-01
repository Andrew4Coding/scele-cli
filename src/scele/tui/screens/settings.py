from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Select, Static

from ..settings import (
    DEFAULT_KEYBINDING_MODE,
    DEFAULT_THEME,
    KEYBINDING_MODE_OPTIONS,
    KEYBINDING_LABELS,
    TuiSettings,
    default_settings,
    is_valid_key,
    key_for_display,
    normalize_key,
)


class SettingsScreen(Screen):
    """Edit the TUI theme and keyboard shortcuts."""

    BINDINGS = [
        Binding("escape", "go_back", "Back", id="navigation.back"),
    ]

    DEFAULT_CSS = """
    #settings-content {
        height: 1fr;
        padding: 1 2;
    }
    #settings-title {
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }
    #settings-description {
        color: $text-muted;
        margin-bottom: 2;
    }
    #settings-theme-label {
        text-style: bold;
        margin-bottom: 1;
    }
    #settings-theme {
        width: 36;
        margin-bottom: 2;
    }
    #settings-keymap-title {
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }
    .setting-row {
        width: 100%;
        height: 3;
    }
    .setting-label {
        width: 36;
        padding-top: 1;
    }
    .setting-input {
        width: 28;
    }
    #settings-status {
        height: auto;
        min-height: 1;
        margin-top: 1;
        color: $text-muted;
    }
    #settings-buttons {
        width: 100%;
        height: auto;
        align-horizontal: right;
        margin-top: 1;
        padding-bottom: 1;
    }
    """

    def compose(self) -> ComposeResult:
        app_settings = self.app.settings
        theme_options = [
            (name, name)
            for name in sorted(self.app.available_themes)
        ]
        yield Header()
        with VerticalScroll(id="settings-content"):
            yield Static("TUI settings", id="settings-title")
            yield Static(
                "Preferences are stored locally in tui.json. Credentials are never stored here.",
                id="settings-description",
            )
            yield Label("Color theme", id="settings-theme-label")
            yield Select(
                theme_options,
                value=app_settings.theme,
                allow_blank=False,
                id="settings-theme",
            )
            yield Label("Keybinding mode", id="settings-mode-label")
            yield Select(
                KEYBINDING_MODE_OPTIONS,
                value=app_settings.keybinding_mode,
                allow_blank=False,
                id="settings-mode",
            )
            yield Static(
                "Vim mode uses h/j/k/l for back, movement, and selection. Text fields keep normal editing.",
                id="settings-mode-description",
            )
            yield Static("Keyboard shortcuts", id="settings-keymap-title")
            for action, label in KEYBINDING_LABELS:
                input_id = self._input_id(action)
                with Horizontal(classes="setting-row"):
                    yield Label(label, classes="setting-label")
                    yield Input(
                        value=key_for_display(app_settings.keymap[action]),
                        id=input_id,
                        classes="setting-input",
                    )
            yield Label("Changes apply when you press Save.", id="settings-status")
            with Horizontal(id="settings-buttons"):
                yield Button("Reset defaults", id="settings-reset")
                yield Button("Cancel", id="settings-cancel")
                yield Button("Save", variant="success", id="settings-save")
        yield Footer()

    @on(Button.Pressed, "#settings-cancel")
    def cancel_button(self) -> None:
        self.action_go_back()

    @on(Button.Pressed, "#settings-reset")
    def reset_button(self) -> None:
        defaults = default_settings()
        self.query_one("#settings-theme", Select).value = DEFAULT_THEME
        self.query_one("#settings-mode", Select).value = DEFAULT_KEYBINDING_MODE
        for action, _label in KEYBINDING_LABELS:
            self.query_one(f"#{self._input_id(action)}", Input).value = key_for_display(
                defaults.keymap[action]
            )
        self._set_status("Defaults loaded. Press Save to apply them.")

    @on(Button.Pressed, "#settings-save")
    def save_button(self) -> None:
        theme = self.query_one("#settings-theme", Select).value
        if not isinstance(theme, str) or theme not in self.app.available_themes:
            self._set_status("Choose a valid color theme.", error=True)
            return

        keybinding_mode = self.query_one("#settings-mode", Select).value
        valid_modes = {mode for _label, mode in KEYBINDING_MODE_OPTIONS}
        if not isinstance(keybinding_mode, str) or keybinding_mode not in valid_modes:
            self._set_status("Choose a valid keybinding mode.", error=True)
            return

        keymap = {}
        invalid = []
        for action, label in KEYBINDING_LABELS:
            value = self.query_one(f"#{self._input_id(action)}", Input).value
            if not is_valid_key(value):
                invalid.append(label)
            else:
                keymap[action] = normalize_key(value)
        if invalid:
            self._set_status(
                "Invalid shortcut: " + ", ".join(invalid[:2]) + ("..." if len(invalid) > 2 else ""),
                error=True,
            )
            return

        try:
            self.app.apply_settings(
                TuiSettings(
                    theme=theme,
                    keybinding_mode=keybinding_mode,
                    keymap=keymap,
                )
            )
        except (OSError, ValueError) as exc:
            self._set_status(f"Could not save settings: {exc}", error=True)
            return
        self.app.notify("Settings saved", severity="information")
        self.dismiss(None)

    def action_go_back(self) -> None:
        self.dismiss(None)

    def _set_status(self, message: str, *, error: bool = False) -> None:
        status = self.query_one("#settings-status", Label)
        status.update(message)
        status.set_class(error, "error-text")

    @staticmethod
    def _input_id(action: str) -> str:
        return "setting-" + action.replace(".", "-")
