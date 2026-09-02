from __future__ import annotations

from typing import Sequence

from textual.widgets import DataTable

from ...models import Course


class CourseListTable(DataTable):
    """A pre-configured DataTable for displaying courses."""

    DEFAULT_CSS = """
    CourseListTable {
        height: 1fr;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.cursor_type = "row"

    def on_mount(self) -> None:
        self.add_columns("ID", "Name", "Category")

    def populate(self, courses: Sequence[Course]) -> None:
        """Populate the table with Course objects."""
        self.clear()
        for c in courses:
            self.add_row(c.id, c.name, c.category, key=c.id)
        self.loading = False
