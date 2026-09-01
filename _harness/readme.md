---
role: agent-instruction
scope: project-context
description: Project context and harness overview
---

# scele-cli — Harness Overview

## What is this project?

`scele-cli` is a command-line client for **SCELE** (`https://scele.cs.ui.ac.id`), the Moodle 4.x LMS used by Fakultas Ilmu Komputer, Universitas Indonesia. It is built for both human and programmatic (AI agent) use.

**Every command prints one JSON document to stdout.**

## Tech stack

| Layer | Technology |
|-------|-----------|
| Language | Python ≥ 3.10 |
| CLI framework | Click ≥ 8.1 |
| HTTP | Requests ≥ 2.31 |
| HTML parsing | BeautifulSoup4 ≥ 4.12, lxml ≥ 5.0 |
| Build backend | Hatchling (PEP 517) |
| Binary packaging | PyInstaller ≥ 6.0 |
| Tests | pytest ≥ 8.0 |
| Optional output | PyYAML ≥ 6.0 (`pip install scele-cli[yaml]`) |
| Skill installer | Node.js ≥ 16 (`bin/install-skill.mjs`) |

## Development

```bash
make dev          # venv + editable install with [dev,build]
make test         # pytest -q
make binary       # PyInstaller one-file build → dist/scele
```

## Using `scele` programmatically

### Discover the tool

```bash
scele schema        # full JSON manifest: every command, its args, and its return shape
scele <cmd> --help  # per-command help
```

Treat `scele schema` as the **source of truth** — parse it, don't hard-code command lists.

### Output contract

| Aspect | Detail |
|--------|--------|
| stdout | Exactly one logical document per run. **Plain JSON when piped or redirected**; pretty table on a real terminal. |
| stderr | On failure only: `{"ok": false, "error": "<code>", "message": "<text>"}` |
| exit code | `0` success, `1` any error |
| compact | `-c` **before** the subcommand for single-line JSON: `scele -c courses` |
| format | `-f json` / `-f yaml` / `-f table` to force a format |

Error codes: `not_authenticated`, `login_failed`, `request_failed`.

### Authentication

```bash
scele whoami                     # check session state
scele login                      # interactive (masked password)
SCELE_USERNAME=... SCELE_PASSWORD=... scele login   # non-interactive
```

Wrong credentials → `{"error":"login_failed"}`.
`{"error":"not_authenticated"}` → session expired, run `scele login` again.

### ID flow — from nothing to a specific thing

```
scele courses                 → course id            (e.g. 4234)
scele course 4234             → activities w/ cmid    (forum/assign/resource module ids)
scele forum <forum-cmid>      → discussions w/ id (d)
scele thread <d>              → posts w/ id
```

- `scele forums|assignments|resources <course-id>` are filtered views of `scele course`.
- `scele assignment <cmid>` and `scele download <cmid>` take an activity cmid, not a course id.

### Commands

**Read-only** (safe): `courses`, `categories [--id N]`, `category <id>`, `course <id>`, `forums <id>`, `forum <id>`, `thread <d>`, `assignments <id>`, `assignment <cmid>`, `resources <id>`, `announcements`.

**Writes** (ask the human first; `post`/`reply` also need `--yes`): `enrol`, `subscribe`, `post`, `reply`, `download`.

### Examples

```bash
scele -c courses | jq -r '.[] | "\(.id)\t\(.name)"'
scele -c course 4234 | jq '.[].activities[] | select(.type=="assign")'
scele -c assignment 222043 | jq '.fields["Submission status"]'
scele -c thread 62493 | jq -r '.[] | "\(.author): \(.body)"'
```

### Notes

- Text fields (`body`, `summary`, dates) are human strings scraped from pages, not normalized.
- Output is not paginated — a forum returns all its discussions at once.
- Announcement forums legitimately return `[]` when empty.

## Harness structure

```
_harness/
├── readme.md        ← you are here (project context)
├── catalog.md       ← project structure lookup
├── routing.md       ← task → file mapping
├── rules.md         ← constraints, boundaries, evolution
├── workflow.md      ← execution procedures
└── memory/
    └── project.md   ← shared long-term memory
```

Load only the minimum files needed for your current task. Route before loading.
