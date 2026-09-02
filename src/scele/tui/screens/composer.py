from __future__ import annotations

from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Middle, Vertical, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static, TextArea

from ... import api
from ...session import NotAuthenticatedError


class _ForumComposerModal(ModalScreen[dict[str, object] | None]):
    """Shared confirmation and worker flow for forum writes."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", id="navigation.back"),
    ]

    subject_required = False
    heading = "COMPOSE FORUM MESSAGE"
    confirm_label = "Post"

    DEFAULT_CSS = """
    _ForumComposerModal {
        align: center middle;
    }
    #composer-dialog {
        width: 72;
        height: auto;
        max-height: 90%;
        border: thick $accent;
        background: $surface;
        padding: 1 2;
    }
    #composer-title {
        width: 100%;
        color: $accent;
        text-style: bold;
        margin-bottom: 1;
    }
    #composer-message {
        height: 12;
        margin-bottom: 1;
    }
    #composer-status {
        height: auto;
        min-height: 1;
        color: $text-muted;
        margin-bottom: 1;
    }
    #composer-buttons {
        width: 100%;
        height: auto;
        align-horizontal: right;
    }
    """

    def compose(self) -> ComposeResult:
        with Middle():
            with Center():
                with Vertical(id="composer-dialog"):
                    yield Static(self.heading, id="composer-title")
                    if self.subject_required:
                        yield Input(placeholder="Subject", id="composer-subject")
                    yield TextArea(
                        placeholder="Write your message...",
                        id="composer-message",
                    )
                    yield Label(
                        "Review the message, then press Post to confirm.",
                        id="composer-status",
                    )
                    with Horizontal(id="composer-buttons"):
                        yield Button("Cancel", id="composer-cancel")
                        yield Button(
                            self.confirm_label,
                            variant="success",
                            id="composer-submit",
                        )

    def on_mount(self) -> None:
        first_input = (
            "#composer-subject" if self.subject_required else "#composer-message"
        )
        self.query_one(first_input).focus()

    @on(Button.Pressed, "#composer-cancel")
    def cancel_button(self) -> None:
        self.action_cancel()

    @on(Button.Pressed, "#composer-submit")
    def submit_button(self) -> None:
        subject = ""
        if self.subject_required:
            subject = self.query_one("#composer-subject", Input).value.strip()
        message = self.query_one("#composer-message", TextArea).text.strip()
        if self.subject_required and not subject:
            self._set_status("A subject is required.", error=True)
            self.query_one("#composer-subject", Input).focus()
            return
        if not message:
            self._set_status("A message is required.", error=True)
            self.query_one("#composer-message", TextArea).focus()
            return

        self.query_one("#composer-submit", Button).disabled = True
        self.query_one("#composer-cancel", Button).disabled = True
        self._set_status("Posting...")
        self._submit(subject, message)

    @work(thread=True)
    def _submit(self, subject: str, message: str) -> None:
        try:
            url = self._request(subject, message)
        except NotAuthenticatedError:
            self.app.call_from_thread(self._finish, None, "Session expired")
        except Exception as exc:  # noqa: BLE001 - display the request failure in the modal
            self.app.call_from_thread(self._finish, None, str(exc))
        else:
            self.app.call_from_thread(self._finish, url, None)

    def _request(self, subject: str, message: str) -> str:
        raise NotImplementedError

    def _finish(self, url: str | None, error: str | None) -> None:
        if error:
            self.query_one("#composer-submit", Button).disabled = False
            self.query_one("#composer-cancel", Button).disabled = False
            self._set_status(f"Error: {error}", error=True)
            return
        self.dismiss({"ok": True, "url": url or ""})

    def _set_status(self, message: str, *, error: bool = False) -> None:
        status = self.query_one("#composer-status", Label)
        status.update(message)
        status.set_class(error, "error-text")

    def action_cancel(self) -> None:
        self.dismiss(None)


class NewDiscussionModal(_ForumComposerModal):
    """Confirmation modal for starting a new discussion."""

    subject_required = True
    heading = "START A NEW DISCUSSION"

    def __init__(self, forum_id: str) -> None:
        super().__init__()
        self.forum_id = forum_id

    def _request(self, subject: str, message: str) -> str:
        session = self.app.session
        if session is None:
            raise RuntimeError("No active SCELE session")
        return api.forum_post(session, self.forum_id, subject, message)


class ReplyModal(_ForumComposerModal):
    """Confirmation modal for replying to a selected forum post."""

    heading = "REPLY TO FORUM POST"
    confirm_label = "Reply"

    def __init__(self, post_id: str, target_label: str | None = None) -> None:
        super().__init__()
        self.post_id = post_id
        self.heading = (
            f"REPLY TO {target_label}" if target_label else "REPLY TO FORUM POST"
        )

    def _request(self, subject: str, message: str) -> str:
        session = self.app.session
        if session is None:
            raise RuntimeError("No active SCELE session")
        return api.forum_reply(session, self.post_id, message)
