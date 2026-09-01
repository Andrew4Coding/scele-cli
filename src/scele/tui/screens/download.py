from __future__ import annotations

from pathlib import Path

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Middle, Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, ProgressBar, Static

from ... import api
from ...session import NotAuthenticatedError


class DownloadModal(ModalScreen[dict[str, object] | None]):
    """Confirm a resource download and show byte-level progress."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", id="navigation.back"),
    ]

    DEFAULT_CSS = """
    DownloadModal {
        align: center middle;
    }
    #download-dialog {
        width: 72;
        height: auto;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }
    #download-title {
        width: 100%;
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }
    #download-target {
        width: 100%;
        color: $text-muted;
        margin-bottom: 1;
    }
    #download-dir {
        margin-bottom: 1;
    }
    #download-progress {
        width: 100%;
        margin-bottom: 1;
    }
    #download-status {
        height: auto;
        min-height: 1;
        color: $text-muted;
        margin-bottom: 1;
    }
    #download-buttons {
        width: 100%;
        height: auto;
        align-horizontal: right;
    }
    """

    def __init__(self, target: str, name: str = "resource") -> None:
        super().__init__()
        self.target = target
        self.resource_name = name or "resource"
        self._active = False

    def compose(self) -> ComposeResult:
        with Middle():
            with Center():
                with Vertical(id="download-dialog"):
                    yield Static("Download course resource", id="download-title")
                    yield Static(self.resource_name, id="download-target")
                    yield Label("Save to directory", classes="form-label")
                    yield Input(value=".", id="download-dir")
                    yield ProgressBar(
                        total=None,
                        show_eta=False,
                        id="download-progress",
                    )
                    yield Label(
                        "Choose a directory, then press Download to confirm.",
                        id="download-status",
                    )
                    with Horizontal(id="download-buttons"):
                        yield Button("Cancel", id="download-cancel")
                        yield Button(
                            "Download",
                            variant="success",
                            id="download-submit",
                        )

    def on_mount(self) -> None:
        self.query_one("#download-dir", Input).focus()

    @on(Button.Pressed, "#download-cancel")
    def cancel_button(self) -> None:
        self.action_cancel()

    @on(Button.Pressed, "#download-submit")
    def submit_button(self) -> None:
        if self._active:
            return
        raw_dir = self.query_one("#download-dir", Input).value.strip() or "."
        out_dir = Path(raw_dir).expanduser()
        if out_dir.exists() and not out_dir.is_dir():
            self._set_status("The destination is not a directory.", error=True)
            self.query_one("#download-dir", Input).focus()
            return

        self._active = True
        self.query_one("#download-submit", Button).disabled = True
        self.query_one("#download-cancel", Button).disabled = True
        self._set_status("Starting download...")
        self._download(out_dir)

    @work(thread=True)
    def _download(self, out_dir: Path) -> None:
        def report(downloaded: int, total: int | None) -> None:
            self.app.call_from_thread(self._update_progress, downloaded, total)

        try:
            session = self.app.session
            if session is None:
                raise RuntimeError("No active SCELE session")
            destination = api.download(
                session,
                self.target,
                out_dir,
                progress=report,
            )
        except NotAuthenticatedError:
            self.app.call_from_thread(self._finish, None, "Session expired")
        except Exception as exc:  # noqa: BLE001 - display request failures in the modal
            self.app.call_from_thread(self._finish, None, str(exc))
        else:
            self.app.call_from_thread(self._finish, destination, None)

    def _update_progress(self, downloaded: int, total: int | None) -> None:
        progress = self.query_one("#download-progress", ProgressBar)
        if total is None:
            progress.update(progress=downloaded)
            self._set_status(f"Downloaded {self._format_bytes(downloaded)}")
        else:
            progress.update(total=total, progress=downloaded)
            self._set_status(
                f"Downloaded {self._format_bytes(downloaded)} of "
                f"{self._format_bytes(total)}"
            )

    def _finish(self, destination: Path | None, error: str | None) -> None:
        self._active = False
        if error:
            self.query_one("#download-submit", Button).disabled = False
            self.query_one("#download-cancel", Button).disabled = False
            self._set_status(f"Error: {error}", error=True)
            return
        self.dismiss({"ok": True, "path": str(destination)})

    def _set_status(self, message: str, *, error: bool = False) -> None:
        status = self.query_one("#download-status", Label)
        status.update(message)
        status.set_class(error, "error-text")

    def action_cancel(self) -> None:
        if not self._active:
            self.dismiss(None)

    @staticmethod
    def _format_bytes(value: int) -> str:
        size = float(value)
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024 or unit == "GB":
                return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
            size /= 1024
        return f"{value} B"
