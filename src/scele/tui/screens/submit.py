"""Assignment detail + submission: AssignmentDetailScreen (instructions +
attachments) and SubmitModal (online text or a local file, confirm-guarded).
"""

from __future__ import annotations

import os

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, DataTable, Footer, Header, Input, Label, RadioButton, RadioSet, Static, TextArea

from ... import api
from ...session import NotAuthenticatedError


class AssignmentDetailScreen(Screen):
    """An assignment's instructions, due dates and brief attachments."""

    BINDINGS = [
        Binding("escape", "go_back", "Back", id="navigation.back"),
        Binding("backspace", "go_back", "Back", show=False),
        Binding("r", "refresh", "Refresh", id="assignment-detail.refresh"),
    ]

    DEFAULT_CSS = """
    AssignmentDetailScreen #detail-body { height: 1fr; padding: 0 1; }
    AssignmentDetailScreen .info-block {
        background: $surface; border: round $panel-lighten-2;
        padding: 1 2; margin-bottom: 1; height: auto;
    }
    AssignmentDetailScreen #detail-files { height: auto; max-height: 12; }
    """

    def __init__(self, ref: str):
        super().__init__()
        self.ref = ref
        self._attachments: list = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(f"ASSIGNMENT DETAIL · {self.ref}", id="detail-title")
        with VerticalScroll(id="detail-body"):
            yield Static("", id="detail-summary", classes="info-block")
            yield Static("[b]Brief attachments[/b]  [dim](enter = download)[/dim]")
            yield DataTable(id="detail-files")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#detail-files", DataTable)
        table.add_columns("File", "Size")
        table.cursor_type = "row"
        self.query_one("#detail-body").loading = True
        self._load()

    @work(thread=True)
    def _load(self) -> None:
        try:
            info = api.assignment_detail(self.app.session, self.ref)
            self.app.call_from_thread(self._populate, info)
        except NotAuthenticatedError:
            self.app.call_from_thread(self.notify, "Session expired", severity="error")
        except Exception as exc:  # noqa: BLE001
            self.app.call_from_thread(self.notify, f"Error: {exc}", severity="error")

    def _populate(self, info) -> None:
        self.query_one("#detail-body").loading = False
        self._attachments = info.attachments
        self.query_one("#detail-summary", Static).update(
            f"[b]{info.name}[/b]\n"
            f"[cyan]Due:[/cyan] {info.due or '—'}  ({info.due_in or 'no due date'})\n"
            f"[cyan]Cut-off:[/cyan] {info.cutoff or '—'}  "
            f"[cyan]Late allowed:[/cyan] {'yes' if info.allow_late else 'no'}\n"
            f"[cyan]Grade:[/cyan] {info.grade or '—'}  "
            f"[cyan]Team submission:[/cyan] {'yes' if info.team_submission else 'no'}\n\n"
            f"{info.instructions or '[dim](no instructions)[/dim]'}"
        )
        table = self.query_one("#detail-files", DataTable)
        table.clear()
        for i, a in enumerate(self._attachments):
            size = a.get("filesize")
            table.add_row(a.get("filename") or "file",
                          f"{size:,} B" if isinstance(size, int) else "—", key=str(i))
        if not self._attachments:
            table.add_row("—", "no attachments")

    @on(DataTable.RowSelected, "#detail-files")
    def _download(self, event: DataTable.RowSelected) -> None:
        if event.row_key.value is None:
            return
        a = self._attachments[int(event.row_key.value)]
        if not a.get("fileurl"):
            return
        from .download import DownloadModal

        self.app.push_screen(DownloadModal(a["fileurl"], a.get("filename") or "attachment"))

    def action_go_back(self) -> None:
        self.app.pop_screen()

    def action_refresh(self) -> None:
        self.query_one("#detail-body").loading = True
        self._load()


class SubmitModal(ModalScreen[dict | None]):
    """Submit online text or a local file to an assignment."""

    BINDINGS = [Binding("escape", "cancel", "Cancel", id="navigation.back")]
    DEFAULT_CSS = """
    SubmitModal { align: center middle; }
    SubmitModal #submit-dialog {
        width: 78; height: auto; max-height: 90%;
        border: thick $accent; background: $surface; padding: 1 2;
    }
    SubmitModal #submit-text { height: 10; margin: 1 0; }
    SubmitModal #submit-buttons { align-horizontal: right; height: auto; }
    """

    def __init__(self, ref: str, name: str = ""):
        super().__init__()
        self.ref = ref
        self.assignment_name = name

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="submit-dialog"):
            yield Static(f"[b]Submit to {self.assignment_name or ('assignment ' + self.ref)}[/b]")
            with RadioSet(id="submit-mode"):
                yield RadioButton("Online text", value=True, id="mode-text")
                yield RadioButton("Local file", id="mode-file")
            yield TextArea(id="submit-text")
            yield Input(placeholder="Path to file", id="submit-file")
            yield RadioSet(
                RadioButton("Submit for grading", value=True, id="final-grade"),
                RadioButton("Save as draft only", id="final-draft"),
                id="submit-final",
            )
            yield Label("", id="submit-status")
            with Horizontal(id="submit-buttons"):
                yield Button("Cancel", id="submit-cancel")
                yield Button("Submit", variant="warning", id="submit-go")

    def on_mount(self) -> None:
        self.query_one("#submit-file", Input).display = False
        self.query_one("#submit-text", TextArea).focus()

    @on(RadioSet.Changed, "#submit-mode")
    def _switch_mode(self, event: RadioSet.Changed) -> None:
        is_file = event.pressed.id == "mode-file"
        self.query_one("#submit-file", Input).display = is_file
        self.query_one("#submit-text", TextArea).display = not is_file

    @on(Button.Pressed, "#submit-cancel")
    def _cancel(self) -> None:
        self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#submit-go")
    def _go(self) -> None:
        is_file = self.query_one("#submit-mode", RadioSet).pressed_button.id == "mode-file"
        final = self.query_one("#submit-final", RadioSet).pressed_button.id == "final-grade"
        if is_file:
            path = self.query_one("#submit-file", Input).value.strip()
            if not path or not os.path.isfile(os.path.expanduser(path)):
                return self._status("Enter a path to an existing file.", error=True)
            payload = ("file", os.path.expanduser(path))
        else:
            text = self.query_one("#submit-text", TextArea).text.strip()
            if not text:
                return self._status("Write something to submit.", error=True)
            payload = ("text", text)
        self.query_one("#submit-go", Button).disabled = True
        self._status("Submitting for grading…" if final else "Saving draft…")
        self._submit(payload, final)

    @work(thread=True)
    def _submit(self, payload, final: bool) -> None:
        kind, value = payload
        try:
            if kind == "file":
                res = api.submit_file(self.app.session, self.ref, value, final)
            else:
                res = api.submit_text(self.app.session, self.ref, value, final)
        except Exception as exc:  # noqa: BLE001
            self.app.call_from_thread(self._status, str(exc), True)
            self.app.call_from_thread(
                lambda: self.query_one("#submit-go", Button).__setattr__("disabled", False))
        else:
            self.app.call_from_thread(self.dismiss, res)

    def _status(self, message: str, error: bool = False) -> None:
        label = self.query_one("#submit-status", Label)
        label.update(f"[b red]{message}[/b red]" if error else message)
