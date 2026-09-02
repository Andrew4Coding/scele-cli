"""Output rendering: pretty tables for humans, JSON/YAML for machines.

Every command still writes a single logical document to stdout. On a real
terminal the default is a colored table; when piped or redirected it is plain
JSON so existing pipelines (`scele -c courses | jq ...`) keep working. Pass
`-f json`, `-f yaml`, or `-f table` to force a format.
"""

import json as _json
import os
import re
import shutil
import sys

import click

from .models import (
    Activity, Announcement, AssignmentInfo, AssignmentStatus, CalendarEvent, Category,
    Course, CourseDetail, Deadline, Discussion, Grade, Notification, Person, Post,
    Resource, Section,
)

_FLAT_MODELS = (
    Course, Category, Discussion, Activity, Resource, Person, Deadline,
    CalendarEvent, Notification, Grade, AssignmentInfo,
)

try:  # optional dependency
    import yaml as _yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

_ANSI = re.compile(r"\x1b\[[0-9;]*m")


def _plain(obj):
    if isinstance(obj, list):
        return [_plain(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _plain(v) for k, v in obj.items()}
    return obj.to_dict() if hasattr(obj, "to_dict") else obj


def _color_enabled() -> bool:
    if os.environ.get("NO_COLOR") or os.environ.get("CLICOLOR") == "0":
        return False
    if os.environ.get("CLICOLOR_FORCE", "0") not in ("", "0", "false"):
        return True
    return sys.stdout.isatty()


def _echo(text: str = "") -> None:
    """Write to stdout, preserving ANSI codes iff color is enabled."""
    click.echo(text, color=_color_enabled())


# ---------------------------------------------------------------- json/yaml

def _colorize(text: str) -> str:
    """Apply ANSI syntax highlighting to a JSON string."""
    out = []
    i = 0
    while i < len(text):
        if text[i] == '"':
            end = i + 1
            while end < len(text) and text[end] != '"':
                if text[end] == "\\":
                    end += 1
                end += 1
            end += 1
            chunk = text[i:end]
            if i > 0 and text[i - 1] == ":":
                out.append(click.style(chunk, fg="cyan"))
            else:
                out.append(click.style(chunk, fg="green"))
            i = end
        elif text[i] in "{}[]":
            out.append(click.style(text[i], fg="white", bold=True))
            i += 1
        elif text[i] == ",":
            out.append(click.style(text[i], fg="white"))
            i += 1
        elif text[i] == ":":
            out.append(click.style(text[i], fg="white", dim=True))
            i += 1
        elif text[i : i + 4] in ("null", "true"):
            out.append(click.style(text[i : i + 4], fg="magenta", bold=True))
            i += 4
        elif text[i : i + 5] == "false":
            out.append(click.style(text[i : i + 5], fg="magenta", bold=True))
            i += 5
        elif text[i].isdigit() or (text[i] == "-" and i + 1 < len(text) and text[i + 1].isdigit()):
            end = i + 1
            while end < len(text) and (text[end].isdigit() or text[end] in ".eE-+"):
                end += 1
            out.append(click.style(text[i:end], fg="yellow"))
            i = end
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


def _emit_json(obj, compact: bool) -> None:
    text = _json.dumps(
        obj, ensure_ascii=False,
        separators=(",", ":") if compact else (",", ": "),
        indent=None if compact else 2,
    )
    if not compact and _color_enabled():
        text = _colorize(text)
    _echo(text)


def _emit_yaml(obj) -> None:
    if not _HAS_YAML:
        fail("PyYAML is required for -f yaml; install it with `pip install pyyaml`",
             code="request_failed")
    _echo(_yaml.safe_dump(obj, sort_keys=False, allow_unicode=True,
                               default_flow_style=False).rstrip())


# ---------------------------------------------------------------- table

def _fmt(v) -> str:
    if v is None:
        return "—"
    if v is True:
        return "true"
    if v is False:
        return "false"
    if isinstance(v, (dict, list)):
        return _json.dumps(v, ensure_ascii=False, separators=(",", ":"))
    return str(v)


def _plain_len(s: str) -> int:
    return len(_ANSI.sub("", s))


def _fit(s: str, width: int) -> str:
    """Pad or truncate a (possibly styled) string to a fixed width."""
    text = _ANSI.sub("", s)
    if len(text) <= width:
        return s + " " * (width - len(text))
    return s[: max(0, width - 1)] + "…"


_NUMERIC_KEYS = {"id", "cmid", "replies", "course_count", "post_id"}


def _table(rows: list[dict], indent: int = 0) -> None:
    """Render a list of uniform dicts as an aligned column table."""
    if not rows:
        _echo(" " * indent + click.style("(empty)", dim=True))
        return
    keys, seen = [], set()
    for r in rows:
        for k in r:
            if k not in seen:
                seen.add(k)
                keys.append(k)
    preferred = ["id", "cmid", "type", "name", "author", "category", "course_count",
                 "replies", "last_post", "section", "subject", "date", "created",
                 "url", "permalink", "body"]
    keys.sort(key=lambda k: preferred.index(k) if k in preferred else len(preferred))

    header = [click.style(k.upper(), bold=True) for k in keys]
    grid = [[_fmt(r.get(k, "")) for k in keys] for r in rows]

    term_w = shutil.get_terminal_size((80, 24)).columns
    avail = max(10, term_w - 2 - indent)
    ncols = len(keys)

    widths = []
    for ci in range(ncols):
        w = max(_plain_len(header[ci]), *(max(_plain_len(row[ci]), 1) for row in grid))
        widths.append(min(w, max(20, avail // max(ncols, 1))))

    gap = 2 * (ncols - 1)
    total = sum(widths) + gap
    if total > avail:
        scale = (avail - gap) / sum(widths)
        widths = [max(6, int(w * scale)) for w in widths]
        while sum(widths) + gap > avail:
            idx = max(range(ncols), key=lambda i: widths[i])
            widths[idx] -= 1
            if widths[idx] <= 6:
                break

    sep = click.style("─" * (sum(widths) + gap), dim=True)
    pad = " " * indent

    lines = [pad + _join(header, widths, keys), pad + sep]
    for row in grid:
        lines.append(pad + _join(row, widths, keys))
    _echo("\n".join(lines))


def _join(cells: list[str], widths: list[int], keys: list[str]) -> str:
    out = []
    for cell, w, key in zip(cells, widths, keys):
        styled = cell
        if key in _NUMERIC_KEYS and cell not in ("—",):
            styled = click.style(cell, fg="yellow")
        if key in ("url", "permalink") and cell not in ("—",):
            styled = click.style(cell, dim=True)
        align = "right" if key in _NUMERIC_KEYS else "left"
        text = _ANSI.sub("", styled)
        if align == "right" and len(text) < w:
            styled = " " * (w - len(text)) + styled
        out.append(_fit(styled, w))
    return "  ".join(out)


def _kv(d: dict) -> None:
    """Render a flat dict as aligned key: value lines."""
    if not d:
        _echo(click.style("(empty)", dim=True))
        return
    width = max(_plain_len(k) for k in d)
    for k, v in d.items():
        vv = _fmt(v)
        if isinstance(v, (dict, list)):
            _echo(f"{click.style(k, fg='cyan'):<{width}}  "
                       + click.style("(see JSON: -f json)", dim=True))
            _echo(click.style("  " + _json.dumps(v, ensure_ascii=False), dim=True))
        else:
            styled = click.style(vv, fg="yellow") if isinstance(v, (int, bool)) else vv
            _echo(f"{click.style(k, fg='cyan'):<{width}}  {styled}")


def _sections(sections: list[Section]) -> None:
    """Course outline: one heading per section, activities as an indented table."""
    for sec in sections:
        name = sec.name or "(unnamed section)"
        _echo(click.style(f"▸ {name}", bold=True, fg="cyan"))
        if sec.summary:
            _echo(click.style(sec.summary, dim=True))
        if sec.activities:
            _table([_plain(a) for a in sec.activities], indent=2)
        else:
            _echo("  " + click.style("(no activities)", dim=True))
        _echo()


def _posts(posts: list[Post], header: str = "posts") -> None:
    for i, p in enumerate(posts, 1):
        _echo(click.style(f"{i:>2}. {p.subject or '(no subject)'}", bold=True))
        meta = "  ".join(x for x in (p.author, p.created) if x)
        if meta:
            _echo("     " + click.style(meta, fg="yellow"))
        for line in (p.body or "").splitlines():
            if line.strip():
                _echo("     " + line)
        _echo()
    if not posts:
        _echo(click.style(f"(no {header})", dim=True))


def _announcements(items: list[Announcement]) -> None:
    for i, a in enumerate(items, 1):
        _echo(click.style(f"{i:>2}. {a.subject}", bold=True))
        meta = "  ".join(x for x in (a.author, a.date) if x)
        if meta:
            _echo("     " + click.style(meta, fg="yellow"))
        for line in (a.body or "").splitlines():
            if line.strip():
                _echo("     " + line)
        if a.permalink:
            _echo("     " + click.style(a.permalink, dim=True))
        _echo()
    if not items:
        _echo(click.style("(no announcements)", dim=True))


def _assignment(a: AssignmentStatus) -> None:
    _echo(click.style(a.name or "Assignment", bold=True, fg="cyan"))
    _echo(click.style(f"cmid: {a.cmid}", dim=True))
    if a.fields:
        _echo()
        _kv(a.fields)
    if a.files:
        _echo()
        _echo(click.style("files:", bold=True))
        for f in a.files:
            _echo("  • " + click.style(f.get("name", ""), bold=True) + "  "
                       + click.style(f.get("url", ""), dim=True))


def _render(obj) -> None:
    if isinstance(obj, list) and obj and all(isinstance(x, Section) for x in obj):
        _sections(obj)
    elif isinstance(obj, list) and obj and all(isinstance(x, Post) for x in obj):
        _posts(obj)
    elif isinstance(obj, list) and obj and all(isinstance(x, Announcement) for x in obj):
        _announcements(obj)
    elif isinstance(obj, AssignmentStatus):
        _assignment(obj)
    elif isinstance(obj, (CourseDetail, AssignmentInfo)):
        _kv(_plain(obj))
    elif isinstance(obj, list) and obj and all(isinstance(x, _FLAT_MODELS) for x in obj):
        _table([_plain(x) for x in obj])
    elif isinstance(obj, list):
        if obj and all(isinstance(x, dict) for x in obj):
            _table(obj)
        else:
            for i, item in enumerate(obj, 1):
                _echo(f"{i}. {item}")
    elif isinstance(obj, dict):
        _kv(obj)
    elif obj is None:
        _echo(click.style("(no data)", dim=True))
    else:
        _echo(str(obj))


# ---------------------------------------------------------------- entry

def emit(obj, fmt: str = "auto", compact: bool = False) -> None:
    """Render obj as one document.

    fmt: "auto" (table on a terminal, JSON otherwise), "json", "yaml", or "table".
    compact: single-line JSON; implies fmt="json".
    """
    if compact:
        fmt = "json"
    if fmt == "auto":
        fmt = "table" if sys.stdout.isatty() else "json"

    if fmt == "table":
        _render(obj)
    elif fmt == "yaml":
        _emit_yaml(_plain(obj))
    else:
        _emit_json(_plain(obj), compact)


def fail(message: str, code: str = "error") -> None:
    """Print a JSON error document to stderr and exit non-zero."""
    _json.dump({"ok": False, "error": code, "message": message}, sys.stderr, ensure_ascii=False)
    sys.stderr.write("\n")
    raise SystemExit(1)