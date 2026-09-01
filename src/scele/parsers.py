"""BeautifulSoup parsers for each SCELE page type.

Selectors target Moodle 4.x with theme `classic` as captured in moodle_capture/.
Each parser is defensive: missing nodes yield empty strings rather than errors.
"""

import re
from urllib.parse import parse_qs, urljoin, urlparse

from bs4 import BeautifulSoup

from .models import (
    Activity, Announcement, AssignmentStatus, Category, Course, Discussion, Post, Section,
)


def _text(node) -> str:
    return " ".join(node.get_text(" ", strip=True).split()) if node else ""


_BODY_TAIL = re.compile(
    r"\s*(Permalink|Show parent|Reply|Discuss this topic|\(\d+ repl(y|ies) so far\)|Edit|Delete)\b.*$",
    re.IGNORECASE,
)


def _body(node) -> str:
    """Post/announcement body text with Moodle's trailing action links removed."""
    return _BODY_TAIL.sub("", _text(node)).strip()


def _qs(url: str, key: str) -> str:
    return parse_qs(urlparse(url).query).get(key, [""])[0]


def _main(soup: BeautifulSoup):
    return soup.select_one("#region-main") or soup.select_one("[role=main]") or soup


def parse_categories(soup: BeautifulSoup, base: str) -> list[Category]:
    """Parse a course/index.php category tree."""
    out = []
    for div in soup.select("[data-categoryid]"):
        link = div.select_one(".categoryname a, h3 a, a")
        if not link:
            continue
        out.append(Category(
            id=div.get("data-categoryid", ""),
            name=_text(link),
            url=urljoin(base, link.get("href", "")),
        ))
    return out


def parse_course_list(soup: BeautifulSoup, base: str) -> list[Course]:
    """Parse the course boxes on a course/index.php page."""
    out = []
    for box in soup.select(".coursebox"):
        link = box.select_one(".coursename a")
        if not link:
            continue
        out.append(Course(
            id=box.get("data-courseid") or _qs(link.get("href", ""), "id"),
            name=_text(link),
            url=urljoin(base, link.get("href", "")),
        ))
    return out


def parse_my_courses(soup: BeautifulSoup, base: str) -> list[Course]:
    """Parse the course links from the /my/ dashboard."""
    out, seen = [], set()
    for link in soup.select("a[href*='/course/view.php?id=']"):
        cid = _qs(link.get("href", ""), "id")
        name = link.get("title", "").strip() or _text(link)
        if not cid or not name or cid in seen:
            continue
        seen.add(cid)
        out.append(Course(id=cid, name=name, url=urljoin(base, link["href"])))
    return out


def parse_course(soup: BeautifulSoup, base: str) -> list[Section]:
    """Parse sections and their activities from a course/view.php page."""
    main = _main(soup)
    sections = []
    for li in main.select("li.section"):
        name = _text(li.select_one(".sectionname")) or li.get("aria-label", "")
        summary = _text(li.select_one(".summarytext, .summary"))
        acts = []
        for act in li.select("li.activity"):
            classes = act.get("class", [])
            modtype = next((c.split("_", 1)[1] for c in classes if c.startswith("modtype_")), "")
            link = act.select_one(".activityinstance a, a.aalink")
            if not link:
                continue
            inst = act.select_one(".instancename")
            if inst and inst.select_one(".accesshide"):
                inst.select_one(".accesshide").extract()
            acts.append(Activity(
                cmid=(act.get("id", "").replace("module-", "")
                      or _qs(link.get("href", ""), "id")),
                type=modtype,
                name=_text(inst) or _text(link),
                url=urljoin(base, link.get("href", "")),
                section=name,
            ))
        if name or acts:
            sections.append(Section(name=name, summary=summary, activities=acts))
    return sections


def parse_forum(soup: BeautifulSoup, base: str) -> list[Discussion]:
    """Parse the discussion list from a mod/forum/view.php page."""
    out = []
    for row in soup.select("tr.discussion, .discussion[data-region=discussion-list-item]"):
        link = next(
            (a for a in row.select("a[href*='discuss.php?d=']")
             if "parent=" not in a.get("href", "") and _text(a)),
            None,
        )
        if not link:
            continue
        author = row.select_one("td.author, .author")
        replies = None
        rep_cell = row.select_one("td.replies, .replies")
        if rep_cell and re.search(r"\d", _text(rep_cell)):
            replies = int(re.search(r"\d+", _text(rep_cell)).group())
        else:
            for cell in row.select("td"):
                if _text(cell).isdigit():
                    replies = int(_text(cell))
                    break
        out.append(Discussion(
            id=_qs(link.get("href", ""), "d"),
            name=_text(link).replace(" Locked", "").strip(),
            url=urljoin(base, link["href"].split("#")[0]),
            author=_text(author).split(" - ")[0] if author else "",
            replies=replies,
        ))
    return out


def parse_discussion(soup: BeautifulSoup) -> list[Post]:
    """Parse individual posts from a mod/forum/discuss.php page (flat, de-duplicated)."""
    out, seen = [], set()
    for art in soup.select("[data-region=post]"):
        pid = art.get("data-post-id") or art.get("id", "").lstrip("p")
        if not pid or pid in seen:
            continue
        seen.add(pid)
        core = art.select_one("[data-region-content=forum-post-core]") or art
        header = core.find("header")
        subject = _text(header.select_one("h3, h4, .subject")) if header else ""
        author_link = (header.select_one("a[href*='user/view.php']") if header else None)
        author = _text(author_link).split(" - ")[0] if author_link else ""
        created = _text(header.select_one("time")) if header else ""
        body_node = core.select_one(
            ".post-content-container, [data-region-content=forum-post-core] > .row .no-overflow, "
            ".posts-content, .fullpost, .no-overflow"
        )
        out.append(Post(id=pid, author=author, created=created,
                        subject=subject, body=_body(body_node)))
    return out


def parse_assignment(soup: BeautifulSoup, base: str, cmid: str) -> AssignmentStatus:
    """Parse the submission-status table from a mod/assign/view.php page."""
    main = _main(soup)
    name = _text(main.select_one("h2"))
    fields, files = {}, []
    table = soup.select_one(
        "table.generaltable, .submissionstatustable table, [class*=submissionstatustable]"
    )
    for tr in table.select("tr") if table else []:
        cells = tr.select("th, td")
        if len(cells) >= 2:
            key, val = _text(cells[0]), _text(cells[1])
            if key:
                fields[key] = val
    for a in (table.select("a[href*='pluginfile.php']") if table else []):
        files.append({"name": _text(a) or a.get("href", "").rsplit("/", 1)[-1],
                      "url": urljoin(base, a["href"])})
    return AssignmentStatus(cmid=cmid, name=name, fields=fields, files=files)


def parse_announcements(soup: BeautifulSoup, base: str) -> list[Announcement]:
    """Parse dashboard/front-page announcement posts."""
    out, seen = [], set()
    for art in soup.select("[data-region=post], .forumpost, .post, article"):
        subject = _text(art.select_one(".subject, h3, h4"))
        if not subject:
            continue
        author_link = art.select_one("a[href*='user/view.php']")
        date = _text(art.select_one("time, .time, .text-muted"))
        key = (subject, date)
        if key in seen:
            continue
        seen.add(key)
        body_node = art.select_one(
            ".posts-content, .content, .fullpost, .post-content-container, .no-overflow"
        )
        plink = art.select_one("a[href*='discuss.php']")
        out.append(Announcement(
            subject=subject,
            author=_text(author_link).split(" - ")[0] if author_link else "",
            date=date,
            body=_body(body_node),
            permalink=urljoin(base, plink["href"]) if plink else "",
        ))
    return out


def read_sesskey(html: str) -> str:
    """Extract M.cfg.sesskey from any page's inline config."""
    m = re.search(r'"sesskey":"([^"]+)"', html)
    return m.group(1) if m else ""
