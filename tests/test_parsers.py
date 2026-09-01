"""Parser tests run against real captured pages produced by ../scele_cli_recorder.

Set $SCELE_FIXTURES to a moodle_capture/ dir, else the default recorder location is
used. Tests that need fixtures skip when it is absent (e.g. a fresh clone).
"""

import os
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from scele import parsers

CAP = Path(
    os.environ.get("SCELE_FIXTURES")
    or Path(__file__).resolve().parents[2] / "scele_cli_recorder" / "moodle_capture"
)
BASE = "https://scele.cs.ui.ac.id"


def soup(name: str) -> BeautifulSoup:
    return BeautifulSoup((CAP / name).read_text(encoding="utf-8"), "lxml")


@pytest.mark.skipif(not CAP.exists(), reason="no capture fixtures")
def test_categories():
    cats = parsers.parse_categories(soup("root_4.html"), BASE)
    assert cats and all(c.id and c.name for c in cats)


@pytest.mark.skipif(not CAP.exists(), reason="no capture fixtures")
def test_course_list():
    courses = parsers.parse_course_list(soup("course_index_php_categoryid_31.html"), BASE)
    assert len(courses) >= 5
    assert all(c.id and c.url.startswith(BASE) for c in courses)


@pytest.mark.skipif(not CAP.exists(), reason="no capture fixtures")
def test_course_outline():
    sections = parsers.parse_course(soup("course_view_php_id_4234.html"), BASE)
    acts = [a for s in sections for a in s.activities]
    assert sections and acts
    assert {a.type for a in acts} & {"forum", "resource", "assign"}
    assert all(a.url.startswith(BASE) for a in acts)


@pytest.mark.skipif(not CAP.exists(), reason="no capture fixtures")
def test_forum_discussions():
    ds = parsers.parse_forum(soup("mod_forum_view_php_id_221050.html"), BASE)
    assert ds and all(d.id.isdigit() and d.name for d in ds)


@pytest.mark.skipif(not CAP.exists(), reason="no capture fixtures")
def test_discussion_posts():
    posts = parsers.parse_discussion(soup("mod_forum_discuss_php_d_62493.html"))
    assert len(posts) >= 2
    assert all(p.id for p in posts)


@pytest.mark.skipif(not CAP.exists(), reason="no capture fixtures")
def test_assignment_status():
    st = parsers.parse_assignment(soup("course_view_php_id_4234_2.html"), BASE, "222043")
    assert "Submission status" in st.fields
    assert st.files and st.files[0]["url"].startswith(BASE)


@pytest.mark.skipif(not CAP.exists(), reason="no capture fixtures")
def test_sesskey():
    assert parsers.read_sesskey((CAP / "course_view_php_id_4234.html").read_text()) == "btz3644rfg"


def test_schema_manifest():
    from scele.cli import main
    from scele.schema import build

    m = build(main)
    names = {c["name"] for c in m["commands"]}
    assert {"courses", "course", "forum", "thread", "schema"} <= names
    for c in m["commands"]:
        assert c["summary"] and c["returns"] and c["example"]
    assert "Course" in m["models"] and "ActionResult" in m["models"]
