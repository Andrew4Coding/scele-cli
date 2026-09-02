---
role: agent-instruction
scope: project-context
description: Project context and harness overview
---

# scele-cli — Harness Overview

## What is this project?

`scele-cli` is a command-line client for **SCELE** (`https://scele.cs.ui.ac.id`), the Moodle 4.x LMS used by Fakultas Ilmu Komputer, Universitas Indonesia. It is built for both human and programmatic (AI agent) use.

It authenticates by minting a **Moodle mobile web-service token** from `/login/token.php` and drives SCELE through the official web-service API (`/webservice/rest/server.php`). No HTML scraping, no session cookie, no `sesskey`.

**Every command prints one JSON document to stdout.**

## Tech stack

| Layer | Technology |
|-------|-----------|
| Language | Python ≥ 3.10 |
| CLI framework | Click ≥ 8.1 |
| HTTP | Requests ≥ 2.31 |
| SCELE API | Moodle mobile web services (REST/JSON) |
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

Error codes: `not_authenticated`, `login_failed`, `request_failed`, `watch_not_found`.

### Authentication

```bash
scele whoami                     # check token state + identity
scele login                      # interactive (masked password) → mints a web-service token
SCELE_USERNAME=... SCELE_PASSWORD=... scele login   # non-interactive
```

`login` POSTs the password to `/login/token.php`; only the resulting token is stored
(`~/.config/scele/token.json`), never the password. Wrong credentials → `{"error":"login_failed"}`.
`{"error":"not_authenticated"}` → the token was rejected, run `scele login` again.
An account behind an external SSO login page cannot mint a token this way.

### ID flow — from nothing to a specific thing

```
scele courses                 → course id            (e.g. 4234)
scele course 4234             → activities w/ cmid    (assignment / resource module ids)
scele forums 4234             → forum cmid
scele forum <forum-cmid>      → discussions w/ id (d)
scele thread <d>              → posts w/ id + parent
```

- `scele assignment <cmid>` / `scele download <cmid>` take an activity cmid.
- `scele assignment-detail` / `scele submit` take an assignment ref (instance id *or* cmid).

### Commands

**Read-only** (safe): `courses`, `course-detail <id>`, `people <id>`, `grades <id>`,
`course-updates <id>`, `deadlines`, `calendar`, `notifications`, `categories [--id N]`,
`category <id>`, `course <id>`, `forums <id>`, `forum <id>`, `thread <d>`,
`assignments <id>`, `assignment <cmid>`, `assignment-detail <ref>`,
`quizzes <id>`, `quiz <cmid>`, `quiz-review <attempt>`, `quiz-attempt <attempt>`, `resources <id>`, `announcements`.

**Writes** (ask the human first; `post`/`reply`/`submit` also need `--yes`): `enrol`,
`subscribe`, `post`, `reply`, `submit`, `download`.

### Examples

```bash
scele -c courses | jq -r '.[] | "\(.id)\t\(.name)"'
scele -c course 4234 | jq '.[].activities[] | select(.type=="assign")'
scele -c assignment 222043 | jq '.fields["Submission status"]'
scele -c thread 62493 | jq -r '.[] | "\(.author): \(.body)"'
```

### Notes

- Dates are rendered `YYYY-MM-DD HH:MM WIB`; HTML bodies are flattened to plain text.
- `forum` / `announcements` take a `--limit`; `thread` returns the whole thread.
- A `news` forum with no posts legitimately returns `[]`.

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
