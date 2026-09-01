---
name: scele
description: >-
  Use when the user wants to read or act on SCELE — the Moodle at Fakultas Ilmu Komputer
  Universitas Indonesia (scele.cs.ui.ac.id). Covers listing their courses, browsing the
  course catalog, reading a course outline, listing forum discussions and reading threads,
  checking assignment submission status and due dates, listing/downloading course resources,
  reading dashboard announcements, and self-enrolling. Backed by the `scele` CLI, which
  returns JSON. Triggers: "my scele", "scele courses", "check my assignment on scele",
  "what's due", "read the discussion forum", "download the slides from scele".
---

# scele

`scele` is a command-line client for SCELE (Moodle at Fasilkom UI). Every command prints
**one JSON document to stdout**; errors print `{"ok":false,"error":<code>,"message":...}`
to stderr and exit non-zero.

## First: is it installed?

```bash
scele --version
```

If missing, install it (needs Python 3.10+):

```bash
npx scele-skill --with-cli        # or, from the repo: ./install.sh  /  .\install.ps1
```

## Discover commands at runtime

```bash
scele schema        # full JSON manifest: every command, its args, its return shape
```

Treat `scele schema` as the source of truth — parse it rather than hard-coding.

## Auth

```bash
scele whoami                       # {"ok":true,"authenticated":true,...} when ready
scele login                        # prompts username + password (no browser, no CAPTCHA)
SCELE_USERNAME=.. SCELE_PASSWORD=.. scele login    # non-interactive
```

`login` needs the human's credentials. If any command returns `{"error":"not_authenticated"}`,
the session expired — ask the user to run `scele login` again. Wrong password → `login_failed`.

## ID flow

```
scele courses                  -> course id            (e.g. 4234)
scele course 4234              -> activities w/ cmid    (forum / assign / resource module ids)
scele forum <forum-cmid>       -> discussions w/ id (d)
scele thread <d>               -> posts
```

`forums`, `assignments`, `resources <course-id>` are filtered views of `course`.
`assignment <cmid>` and `download <cmid>` take an activity cmid, not a course id.

## Commands

Read-only: `courses`, `categories [--id N]`, `category <id>`, `course <id>`, `forums <id>`,
`forum <id>`, `thread <d>`, `assignments <id>`, `assignment <cmid>`, `resources <id>`,
`announcements`, `schema`, `whoami`.

Writes — confirm with the user first; `post`/`reply` also need `--yes`:
`enrol <course> --instance N [--key K]`, `subscribe <forum> [--discussion d]`,
`post <forum> --subject S --message M --yes`, `reply <post> --message M --yes`,
`download <cmid|url> [-o dir]`.

## Examples

```bash
scele -c courses | jq -r '.[] | "\(.id)\t\(.name)"'
scele -c course 4234 | jq '.[].activities[] | select(.type=="assign")'
scele -c assignment 222043 | jq '.fields'
scele -c thread 62493 | jq -r '.[] | "\(.author): \(.body)"'
```

`-c` (before the subcommand) gives single-line JSON.

## Notes

- Text fields (`body`, dates, `summary`) are human strings scraped from pages, not normalized.
- An empty forum (e.g. "Class Announcements" with no posts) legitimately returns `[]`.
- Output is never paginated — a forum returns all its discussions at once.
- Never pass credentials on the command line; use the prompt or the env vars.
