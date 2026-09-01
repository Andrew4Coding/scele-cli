# Using `scele` from an AI agent

`scele` is a command-line client for SCELE (the Moodle at Fasilkom UI). It is built for
programmatic use: **every command prints one JSON document to stdout.**

## Discover the tool

```bash
scele schema        # full JSON manifest: every command, its args, and its return shape
scele <cmd> --help  # per-command help
```

Treat `scele schema` as the source of truth — parse it, don't hard-code command lists.

## Contract

| | |
|---|---|
| stdout | exactly one logical document per run; **plain JSON when piped or redirected** (safe to pipe straight into a parser), pretty table on a real terminal |
| stderr | on failure only: `{"ok": false, "error": "<code>", "message": "<text>"}` |
| exit code | `0` success, `1` any error |
| compact | put `-c` **before** the subcommand for single-line JSON: `scele -c courses` |
| format  | `-f json` / `-f yaml` / `-f table` to force a format; `-f yaml` needs PyYAML (`pip install scele-cli[yaml]`) |

Error codes: `not_authenticated`, `login_failed`, `request_failed`.

## Auth

```bash
scele whoami                     # {"ok":true,"authenticated":true,...} if ready
scele login                      # prompts for username + password (no browser, no CAPTCHA)
```

Non-interactive:

```bash
SCELE_USERNAME=... SCELE_PASSWORD=... scele login
```

Wrong credentials → `{"error":"login_failed"}`. If a command returns
`{"error":"not_authenticated"}`, the session expired — run `scele login` again.

## ID flow (how to get from nothing to a specific thing)

```
scele courses                 -> course id            (e.g. 4234)
scele course 4234             -> activities w/ cmid    (forum/assign/resource module ids)
scele forum <forum-cmid>      -> discussions w/ id (d)
scele thread <d>              -> posts w/ id
```

- `scele forums|assignments|resources <course-id>` are filtered views of `scele course`.
- `scele assignment <cmid>` and `scele download <cmid>` take an activity cmid, not a course id.

## Commands

Read-only: `courses`, `categories [--id N]`, `category <id>`, `course <id>`, `forums <id>`,
`forum <id>`, `thread <d>`, `assignments <id>`, `assignment <cmid>`, `resources <id>`,
`announcements`.

Writes (ask the human first; `post`/`reply` also need `--yes` to skip their prompt):
`enrol <course> --instance N [--key K]`, `subscribe <forum> [--discussion d]`,
`post <forum> --subject S --message M --yes`, `reply <post> --message M --yes`,
`download <cmid|url> [-o dir]`.

## Examples

```bash
scele -c courses | jq -r '.[] | "\(.id)\t\(.name)"'
scele -c course 4234 | jq '.[].activities[] | select(.type=="assign")'
scele -c assignment 222043 | jq '.fields["Submission status"]'
scele -c thread 62493 | jq -r '.[] | "\(.author): \(.body)"'
```

## Notes

- Text fields (`body`, `summary`, dates) are human strings scraped from pages, not normalized.
- Output is not paginated — a forum returns all its discussions at once.
- Announcement forums (e.g. "Class Announcements") legitimately return `[]` when empty.
