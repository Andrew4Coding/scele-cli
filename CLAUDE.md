# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`scele` — a command-line client for **SCELE** (`https://scele.cs.ui.ac.id/`), the Moodle instance of
Fakultas Ilmu Komputer, Universitas Indonesia. It logs in over HTTP with a username/password, stores
the session cookie, and scrapes Moodle pages into JSON.

The page-capture tooling used to reverse-engineer SCELE's HTML lives in the sibling repo
`../scele_cli_recorder/` (Playwright recorder + HTML cleaner + `moodle_capture/` fixtures). It is not
a dependency of this CLI.

## Layout

- `src/scele/` — the package (`scele` entry point):
  - `cli.py` — click command surface. `_guard()` wraps every API call so any exception becomes a JSON
    error. `_out()` prints via `output.emit`.
  - `api.py` — one function per command; takes a `SceleSession`.
  - `session.py` — authed `requests.Session`; `get()` raises `NotAuthenticatedError` on a login redirect.
  - `parsers.py` — one BeautifulSoup parser per Moodle page type. Defensive: missing nodes → "".
  - `auth.py` — `terminal_login`: GET `/login/index.php` for the `logintoken` hidden field, POST
    username+password, verify with GET `/my/`. Reads creds from prompt (password hidden) or
    `SCELE_USERNAME`/`SCELE_PASSWORD`. Password never written to disk; only saved on verified success;
    failure → `login_failed` and the existing cookie file is left untouched.
  - `models.py` — dataclasses with `to_dict()`.
  - `output.py` — `emit` (one JSON doc to stdout), `fail` (JSON error to stderr, exit 1).
  - `config.py` — cookie store. `~/.config/scele/` (or `$XDG_CONFIG_HOME`) on Unix,
    `%APPDATA%\scele\` on Windows; override with `SCELE_CONFIG_DIR`. Base URL: `SCELE_BASE_URL`.
- `install.sh` (Linux/macOS/WSL/Git-Bash) and `install.ps1` (Windows) — bootstrap pip+pipx and
  `pipx install` this dir. Flags: `--editable`, `--from <path|git-url>`, `--uninstall`.
  `Makefile` targets just call `install.sh`.
- `skills/scele/SKILL.md` — the Agent Skill (condensed `AGENTS.md` in skill format). Installs via
  `npx skills add Andrew4Coding/scele-cli` (the vercel-labs `skills` CLI discovers it at
  `skills/*/SKILL.md`), or `npx scele-skill` (`bin/install-skill.mjs`, zero deps, `--with-cli` also
  runs the CLI installer). Keep SKILL.md, `AGENTS.md`, and `schema.py` in sync when commands change.
  `SKILLS.md` documents all install methods.
  - `schema.py` — builds the `scele schema` manifest by introspecting the click group + dataclasses.
- `ENDPOINTS.md` — Moodle endpoint map + per-page component structure (derived from the recorder's captures).
- `AGENTS.md` — how to drive `scele` programmatically. Keep in sync with the CLI.
- `tests/test_parsers.py` — runs parsers against real captures at
  `../scele_cli_recorder/moodle_capture/` (or `$SCELE_FIXTURES`); fixture-dependent tests skip if absent.

## Output contract (do not break)

- Every command prints **exactly one JSON document to stdout** via `output.emit`.
- Errors go to **stderr** as `{"ok": false, "error": <code>, "message": ...}` via `output.fail`, exit 1.
  Codes: `not_authenticated`, `login_failed`, `request_failed`.
- No human/table mode. Never `print`/`click.echo` prose to stdout; prompts and notices go to stderr.
- `-c/--compact` is a group-level flag for single-line JSON.

## Working on the CLI

```bash
make dev            # python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
make test           # .venv/bin/pytest -q
./install.sh -e     # pipx editable install (puts `scele` on PATH)
```

- Parser selectors target Moodle 4.x, theme `classic`. When SCELE's HTML changes: re-capture with
  `../scele_cli_recorder`, run its `clean_capture.py`, then fix `parsers.py` until `pytest` passes.
- `parse_my_courses`, `parse_forum`, `parse_discussion`, `parse_announcements` were tuned against a
  live session; `pytest` only covers the older capture markup for them.
- State-changing ops (`enrol`, `post`, `reply`, `subscribe`) need `sesskey` + form hidden fields;
  `api._hidden()` scrapes them from the GET form first. `post`/`reply` require `--yes` or a TTY prompt.
- When you add/rename a command, update `RETURNS` and `EXAMPLES` in `schema.py`
  (`test_schema_manifest` enforces both) and the command list in `AGENTS.md`.

## Notes

- Some forums (e.g. "Class Announcements") legitimately return `[]` — they have no discussions.
- Captured HTML in the recorder repo contains other students' personal data; keep it local.
