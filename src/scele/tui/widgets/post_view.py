from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static

from ...models import Announcement, Post


class PostView(Widget):
    """A widget that renders a single forum post."""

    can_focus = True

    DEFAULT_CSS = """
    PostView {
        height: auto;
        margin: 0 1;
        padding: 1 2;
        border: solid $accent;
        background: $surface;
        margin-bottom: 1;
    }
    PostView:focus {
        border: round $accent;
        background: $surface-lighten-1;
    }
    PostView .post-header {
        text-style: bold;
        color: $text;
    }
    PostView .post-meta {
        color: $text-muted;
        text-style: italic;
    }
    PostView .post-body {
        margin-top: 1;
    }
    PostView .post-index {
        color: $accent;
        text-style: bold;
    }
    """

    def __init__(self, post: Post | Announcement, index: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.post = post
        self.index = index

    def on_mount(self) -> None:
        depth = getattr(self.post, "depth", 0) or 0
        if depth:
            self.styles.margin = (0, 1, 1, min(depth, 8) * 3 + 1)

    class Selected(Message):
        """Posted when the user focuses a post to reply to it."""

        def __init__(self, post_view: "PostView") -> None:
            super().__init__()
            self.post = post_view.post

    def on_focus(self) -> None:
        self.post_message(self.Selected(self))

    def on_click(self) -> None:
        self.post_message(self.Selected(self))

    def compose(self) -> ComposeResult:
        post = self.post
        if isinstance(post, Post):
            depth = getattr(post, "depth", 0) or 0
            marker = f"#{self.index}" + ("  [dim]↳ reply[/dim]" if depth else "")
            yield Static(marker, classes="post-index")
            yield Static(f"{post.subject or '(no subject)'}", classes="post-header")
            meta_parts = [x for x in (post.author, post.created) if x]
            yield Static(" — ".join(meta_parts), classes="post-meta")
            yield Static(post.body or "", classes="post-body")
        elif isinstance(post, Announcement):
            yield Static(f"#{self.index}", classes="post-index")
            yield Static(f"{post.subject}", classes="post-header")
            meta_parts = [x for x in (post.author, post.date) if x]
            yield Static(" — ".join(meta_parts), classes="post-meta")
            yield Static(post.body or "", classes="post-body")
            if post.permalink:
                yield Static(f"[dim]{post.permalink}[/dim]", classes="post-meta")
