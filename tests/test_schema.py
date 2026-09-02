"""The `scele schema` manifest stays complete and in sync with the CLI."""

from scele.cli import main
from scele.schema import build


def test_schema_manifest_is_complete():
    m = build(main)
    names = {c["name"] for c in m["commands"]}
    assert {"courses", "course", "forum", "thread", "grades",
            "deadlines", "notifications", "schema"} <= names
    for c in m["commands"]:
        assert c["summary"] and c["returns"] and c["example"]
    assert "Course" in m["models"] and "ActionResult" in m["models"]


def test_every_command_has_returns_and_example():
    from scele.schema import EXAMPLES, RETURNS

    for name in {c["name"] for c in build(main)["commands"]}:
        if name == "schema":
            continue
        assert name in RETURNS, f"{name} missing from schema.RETURNS"
        assert name in EXAMPLES, f"{name} missing from schema.EXAMPLES"
