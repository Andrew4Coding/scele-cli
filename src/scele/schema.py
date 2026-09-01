"""Self-describing manifest so an agent can discover every command and its I/O shape.

`scele schema` prints this as JSON. Keep RETURNS / EXAMPLES in sync when adding commands.
"""

import dataclasses

from . import __version__, models
from .config import base_url

RETURNS: dict[str, str] = {
    "login": "ActionResult",
    "logout": "ActionResult",
    "whoami": "{ok: bool, authenticated: bool, base_url: string, sesskey: string}",
    "courses": "Course[]",
    "categories": "Category[]",
    "category": "Course[]",
    "course": "Section[]",
    "forums": "Activity[]",
    "forum": "Discussion[]",
    "thread": "Post[]",
    "assignments": "Activity[]",
    "assignment": "AssignmentStatus",
    "resources": "Activity[]",
    "announcements": "Announcement[]",
    "enrol": "ActionResult",
    "subscribe": "ActionResult",
    "post": "ActionResult & {url: string}",
    "reply": "ActionResult & {url: string}",
    "download": "ActionResult & {path: string}",
    "schema": "this document",
}

EXAMPLES: dict[str, str] = {
    "courses": "scele courses",
    "categories": "scele categories --id 31",
    "category": "scele category 176",
    "course": "scele course 4234",
    "forums": "scele forums 4234",
    "forum": "scele forum 222560",
    "thread": "scele thread 62493",
    "assignments": "scele assignments 4234",
    "assignment": "scele assignment 222043",
    "resources": "scele resources 4234",
    "announcements": "scele announcements",
    "enrol": "scele enrol 4128 --instance 6339 --key secret",
    "subscribe": "scele subscribe 17474 --discussion 62493",
    "post": "scele post 17474 --subject 'Hi' --message 'Hello' --yes",
    "reply": "scele reply 553756 --message 'Thanks' --yes",
    "download": "scele download 222038 -o ./dl",
}

_PY_TO_JSON = {str: "string", int: "integer", float: "number", bool: "boolean", dict: "object"}


def _type_name(tp) -> str:
    if tp in _PY_TO_JSON:
        return _PY_TO_JSON[tp]
    origin = getattr(tp, "__args__", None)
    if origin:
        inner = [a for a in origin if a is not type(None)]
        base = str(getattr(tp, "__origin__", "")).replace("<class '", "").replace("'>", "")
        if base == "list":
            return f"{_type_name(inner[0])}[]"
        if base == "dict":
            return f"map<{_type_name(inner[0])}, {_type_name(inner[1])}>"
        if len(inner) == 1:
            return f"{_type_name(inner[0])}?"
    return getattr(tp, "__name__", str(tp))


def _models() -> dict[str, dict]:
    out = {}
    for name in dir(models):
        obj = getattr(models, name)
        if dataclasses.is_dataclass(obj) and isinstance(obj, type):
            out[name] = {f.name: _type_name(f.type) for f in dataclasses.fields(obj)}
    if "AssignmentStatus" in out:
        out["AssignmentStatus"]["files"] = "{name: string, url: string}[]"
    out["ActionResult"] = {"ok": "boolean", "action": "string", "...": "command-specific fields"}
    return out


def build(group) -> dict:
    """Introspect the click command group into a JSON-serializable manifest."""
    commands = []
    for name, cmd in sorted(group.commands.items()):
        args, opts = [], []
        for p in cmd.params:
            entry = {"name": p.name, "required": bool(getattr(p, "required", False))}
            if p.param_type_name == "argument":
                args.append(entry)
            else:
                entry["flags"] = list(p.opts)
                entry["is_flag"] = bool(getattr(p, "is_flag", False))
                if getattr(p, "help", None):
                    entry["help"] = p.help
                opts.append(entry)
        commands.append({
            "name": name,
            "summary": (cmd.help or "").strip().split("\n")[0],
            "arguments": args,
            "options": opts,
            "returns": RETURNS.get(name, "object"),
            "example": EXAMPLES.get(name, f"scele {name}"),
        })
    return {
        "tool": "scele",
        "version": __version__,
        "description": "Read/write client for SCELE (Moodle) at Fasilkom UI.",
        "base_url": base_url(),
        "output_contract": {
            "stdout": "exactly one JSON document per invocation (array or object)",
            "stderr": "on failure: {\"ok\": false, \"error\": <code>, \"message\": <text>}",
            "exit_code": "0 on success, 1 on any error",
            "compact_flag": "-c / --compact (before the subcommand) for single-line JSON",
        },
        "auth": {
            "setup": "scele login  (prompts for username + password; no browser, no CAPTCHA)",
            "non_interactive": "set SCELE_USERNAME and SCELE_PASSWORD, then run `scele login`",
            "check": "scele whoami",
            "store": "~/.config/scele/cookies.json",
            "error_code": "not_authenticated",
        },
        "error_codes": [
            "not_authenticated", "login_failed", "request_failed",
        ],
        "id_conventions": {
            "course id": "from `scele courses` / URLs `course/view.php?id=<course>`",
            "cmid (activity/module id)": "from `scele course <id>`; used by forum/assignment/resource",
            "forum id": "the cmid of a forum activity -> `scele forum <cmid>`",
            "discussion id (d)": "from `scele forum <cmid>` -> `scele thread <d>`",
            "post id": "from `scele thread <d>` -> `scele reply <post>`",
        },
        "commands": commands,
        "models": _models(),
    }
