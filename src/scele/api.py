"""High-level SCELE operations built on SceleSession + parsers."""

from pathlib import Path
from urllib.parse import urljoin

from . import parsers
from .models import Activity, Section
from .session import SceleSession


def my_courses(s: SceleSession):
    """Return the courses shown on the user's dashboard."""
    return parsers.parse_my_courses(s.soup("/my/"), s.base)


def categories(s: SceleSession, category_id: str | None = None):
    """Return course categories, optionally scoped to a parent category."""
    params = {"categoryid": category_id} if category_id else None
    return parsers.parse_categories(s.soup("/course/index.php", params), s.base)


def courses_in_category(s: SceleSession, category_id: str):
    """Return the courses listed under a category."""
    soup = s.soup("/course/index.php", {"categoryid": category_id})
    return parsers.parse_course_list(soup, s.base)


def course(s: SceleSession, course_id: str) -> list[Section]:
    """Return the section/activity outline of a course."""
    soup = s.soup("/course/view.php", {"id": course_id})
    return parsers.parse_course(soup, s.base)


def _activities(s: SceleSession, course_id: str, modtype: str) -> list[Activity]:
    return [a for sec in course(s, course_id) for a in sec.activities if a.type == modtype]


def forums(s: SceleSession, course_id: str):
    """Return the forum activities in a course."""
    return _activities(s, course_id, "forum")


def resources(s: SceleSession, course_id: str):
    """Return file/folder resource activities in a course."""
    return [a for sec in course(s, course_id) for a in sec.activities
            if a.type in ("resource", "folder")]


def assignments(s: SceleSession, course_id: str):
    """Return the assignment activities in a course."""
    return _activities(s, course_id, "assign")


def forum(s: SceleSession, forum_id: str):
    """Return the discussion list of a forum."""
    return parsers.parse_forum(s.soup("/mod/forum/view.php", {"id": forum_id}), s.base)


def thread(s: SceleSession, discussion_id: str):
    """Return the posts in a discussion thread."""
    soup = s.soup("/mod/forum/discuss.php", {"d": discussion_id})
    return parsers.parse_discussion(soup)


def assignment(s: SceleSession, cmid: str):
    """Return the submission status of an assignment."""
    soup = s.soup("/mod/assign/view.php", {"id": cmid})
    return parsers.parse_assignment(soup, s.base, cmid)


def announcements(s: SceleSession):
    """Return the front-page / dashboard announcements."""
    return parsers.parse_announcements(s.soup("/"), s.base)


def enrol(s: SceleSession, course_id: str, instance_id: str, key: str = "") -> bool:
    """Self-enrol into a course; returns True on an apparent success."""
    data = {
        "id": course_id,
        "instance": instance_id,
        "sesskey": s.sesskey(),
        f"_qf__enrol_self_enrol_form_{instance_id}": "1",
        f"_qf__{instance_id}_enrol_self_enrol_form": "1",
        "enrolpassword": key,
        "submitbutton": "Enrol me",
    }
    resp = s.post("/enrol/index.php", data=data, params={"id": course_id})
    return "/course/view.php" in resp.url or "You are enrolled" in resp.text


def forum_subscribe(s: SceleSession, forum_id: str, discussion_id: str | None = None) -> bool:
    """Toggle subscription to a forum or a single discussion."""
    params = {"id": forum_id, "sesskey": s.sesskey()}
    if discussion_id:
        params["d"] = discussion_id
    resp = s.get("/mod/forum/subscribe.php", params=params)
    return resp.status_code == 200


def forum_post(s: SceleSession, forum_id: str, subject: str, message: str) -> str:
    """Start a new discussion in a forum; returns the new discussion URL."""
    page = s.get("/mod/forum/post.php", params={"forum": forum_id})
    itemid = _hidden(page.text, "message[itemid]")
    data = {
        "course": _hidden(page.text, "course"),
        "forum": forum_id,
        "discussion": "0", "parent": "0", "groupid": "", "edit": "0", "reply": "0",
        "sesskey": s.sesskey(),
        "_qf__mod_forum_post_form": "1",
        "subject": subject,
        "message[text]": message,
        "message[format]": "1",
        "message[itemid]": itemid,
        "submitbutton": "Post to forum",
    }
    resp = s.post("/mod/forum/post.php", data=data)
    return resp.url


def forum_reply(s: SceleSession, post_id: str, message: str) -> str:
    """Reply to a forum post; returns the resulting discussion URL."""
    page = s.get("/mod/forum/post.php", params={"reply": post_id})
    itemid = _hidden(page.text, "message[itemid]")
    data = {
        "reply": post_id, "parent": post_id,
        "sesskey": s.sesskey(),
        "_qf__mod_forum_post_form": "1",
        "subject": _hidden(page.text, "subject") or "Re:",
        "message[text]": message,
        "message[format]": "1",
        "message[itemid]": itemid,
        "submitbutton": "Post to forum",
    }
    resp = s.post("/mod/forum/post.php", data=data)
    return resp.url


def download(s: SceleSession, url_or_cmid: str, out_dir: Path) -> Path:
    """Download a pluginfile URL, or resolve a resource cmid then download it."""
    if url_or_cmid.isdigit():
        resp = s.get("/mod/resource/view.php", {"id": url_or_cmid})
        url = resp.url
    else:
        url = urljoin(s.base, url_or_cmid)
    resp = s.http.get(url, params={"forcedownload": "1"}, stream=True, timeout=60)
    resp.raise_for_status()
    name = resp.headers.get("content-disposition", "")
    fname = ""
    if "filename=" in name:
        fname = name.split("filename=", 1)[1].strip('"; ')
    fname = fname or url.rstrip("/").rsplit("/", 1)[-1] or "download"
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / fname
    with open(dest, "wb") as fh:
        for chunk in resp.iter_content(8192):
            fh.write(chunk)
    return dest


def _hidden(html: str, name: str) -> str:
    import re
    m = re.search(
        rf'name="{re.escape(name)}"[^>]*value="([^"]*)"', html
    ) or re.search(rf'value="([^"]*)"[^>]*name="{re.escape(name)}"', html)
    return m.group(1) if m else ""
