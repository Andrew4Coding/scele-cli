from __future__ import annotations

from textual.binding import Binding
from textual.message import Message
from textual.widgets import Input


class SearchBar(Input):
    """A one-line filter box that screens reveal with the find key."""

    DEFAULT_CSS = """
    SearchBar {
        display: none;
        height: auto;
        margin: 0 1;
        border: tall $accent;
        background: $surface;
    }
    SearchBar.-active {
        display: block;
    }
    """

    BINDINGS = [Binding("escape", "close", "Close", show=False)]

    class Dismissed(Message):
        """Posted when the user closes the search bar with Escape."""

        def __init__(self, search_bar: "SearchBar") -> None:
            self.search_bar = search_bar
            super().__init__()

    def __init__(self) -> None:
        super().__init__(placeholder="Filter list — Esc to close", id="search-bar")
        self.can_focus = False

    def open(self) -> None:
        """Reveal the bar and move focus into it."""
        self.can_focus = True
        self.add_class("-active")
        self.focus()

    def action_close(self) -> None:
        """Clear the filter, hide the bar, and tell the screen to restore the list."""
        self.value = ""
        self.remove_class("-active")
        self.can_focus = False
        self.post_message(self.Dismissed(self))


FIND_BINDING = Binding("f", "find", "Find", id="navigation.find")


class SearchableScreen:
    """Mixin: press the find key to filter a screen's primary list in place.

    A screen mixes this in before ``Screen``, adds ``FIND_BINDING`` to its own
    ``BINDINGS`` (Textual ignores ``BINDINGS`` on non-widget mixins), yields
    ``SearchBar()`` in ``compose``, sets ``search_focus`` to the list widget's
    selector, and implements ``filter_list``.
    """

    search_focus: str | None = None

    @property
    def search_query(self) -> str:
        """Current filter text, stripped and lower-cased ("" when inactive)."""
        try:
            return self.query_one(SearchBar).value.strip().lower()
        except Exception:
            return ""

    def action_find(self) -> None:
        self.query_one(SearchBar).open()

    def on_input_changed(self, event: Input.Changed) -> None:
        if isinstance(event.input, SearchBar):
            event.stop()
            self.filter_list(event.value.strip().lower())

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if isinstance(event.input, SearchBar):
            event.stop()
            self._restore_list_focus()

    def on_search_bar_dismissed(self, event: SearchBar.Dismissed) -> None:
        event.stop()
        self.filter_list("")
        self._restore_list_focus()

    def _restore_list_focus(self) -> None:
        if self.search_focus:
            try:
                self.query_one(self.search_focus).focus()
            except Exception:
                pass

    def filter_list(self, query: str) -> None:  # pragma: no cover - overridden
        raise NotImplementedError
