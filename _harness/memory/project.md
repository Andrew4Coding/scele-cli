# Project Memory

> Shared long-term memory for all agents working on scele-cli.
> Low-risk to update — agents may update freely.

## Project identity

- **Name**: scele-cli
- **Repo**: Andrew4Coding/scele-cli
- **Current version**: 0.1.0
- **Base URL**: `https://scele.cs.ui.ac.id`
- **Target platform**: Moodle 4.x (theme *classic*)

## Key decisions

| Decision | Rationale |
|----------|-----------|
| HTML scraping (not Moodle REST API) | SCELE does not grant students API tokens or Mobile Web Service access |
| Stateless CLI — except `watch` | Read/write commands stay one-shot; `watch` adds an opt-in POSIX background daemon that re-runs a command on an interval |
| Multi-channel distribution | Standalone binary (PyInstaller), Python package (pipx/pip), Agent Skill (SKILL.md) |
| Centralized version in `__init__.py` | Consumed by Hatchling, CLI `--version`, and release scripts |
| Fixtures in companion repo | Keeps production CLI free of Playwright/browser automation |

## Known quirks

- Text fields (`body`, `summary`, dates) are human strings scraped from HTML, not normalized.
- Output is not paginated — e.g. a forum returns all discussions at once.
- Announcement forums legitimately return `[]` when empty.
- Parser tests skip gracefully when `$SCELE_FIXTURES` is not set.

## Recent history

- v0.1.0 — initial release baseline
- Added pretty CLI output: default table on TTY, JSON when piped, `-f` format flags
- Added `watch` command group (branch `feat/watch-command`): background monitor for any
  subcommand, exact git-style unified diff of canonical JSON output, webhook notifications.

## `watch` design notes

- State: `~/.config/scele/watches/<name>/` — `watch.json` (config), `state.json`
  (`last_hash` + `last_canonical`), `events.jsonl` (append-only), `daemon.pid`, `daemon.log`.
- Each tick runs `python -m scele -c <command>` as a child process (isolation; reuses all
  auth/parsers). `sesskey` and other volatile keys are stripped before diffing.
- Diff = `difflib.unified_diff`, 3 lines context (git default). Change events carry
  `diff` + `added_lines`/`removed_lines` + full `snapshot`.
- Webhook: plain JSON POST, `--webhook-header` passthrough only (no HMAC), 3 retries w/ backoff.
- **POSIX only** (`os.fork`-style detach via `subprocess` + `start_new_session`). No
  reboot persistence — stale watches show as `stopped` in `watch ls`.

## Open items

- Windows background support for `watch` (deferred).
- Optional `watch resume --all` after reboot (deferred).
