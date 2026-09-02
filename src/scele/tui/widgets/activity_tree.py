from textual.widgets import Tree

from ...models import Activity, Section

TYPE_ICONS = {
    "forum": "◇",
    "assign": "▤",
    "resource": "▦",
    "folder": "▸",
    "url": "↗",
    "page": "≡",
    "quiz": "?",
    "label": "•",
}


class ActivityTree(Tree):
    """A Tree widget pre-configured for displaying course sections and activities."""

    DEFAULT_CSS = """
    ActivityTree {
        height: 1fr;
    }
    """

    def __init__(self, **kwargs):
        super().__init__("Course Outline", **kwargs)

    def populate(self, sections: list[Section]) -> None:
        """Populate the tree with sections and their activities."""
        self.clear()
        self.root.expand()
        for sec in sections:
            label = f"▸ {sec.name}" if sec.name else "▸ (unnamed)"
            node = self.root.add(label, expand=True)
            if sec.summary:
                node.add_leaf(f"[dim]{sec.summary[:100]}[/dim]")
            for act in sec.activities:
                icon = TYPE_ICONS.get(act.type, "·")
                node.add_leaf(f"{icon} [{act.type}] {act.name}", data=act)
        self.loading = False
