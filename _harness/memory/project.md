# Project Memory

> Shared long-term memory for all agents working on scele-cli.
> Low-risk to update — agents may update freely.

## Project identity

- **Name**: scele-cli
- **Repo**: Andrew4Coding/scele-cli
- **Current version**: 0.2.0
- **Base URL**: `https://scele.cs.ui.ac.id`
- **Target platform**: Moodle 4.x, mobile web-service API

## Key decisions

| Decision | Rationale |
|----------|-----------|
| Moodle mobile web-service API (v0.2.0) | `/login/token.php` accepts a password on SCELE; the WS API is stable JSON — no HTML breakage. Replaced the scraping layer (`parsers.py`, bs4/lxml) entirely. |
| Token-only storage | The password is exchanged for a token at `login` and never persisted; `token.json` holds only the token. |
| Stateless CLI — except `watch` | Read/write commands stay one-shot; `watch` adds an opt-in POSIX background daemon that re-runs a command on an interval |
| Multi-channel distribution | Standalone binary (PyInstaller), Python package (pipx/pip), Agent Skill (SKILL.md) |
| Centralized version in `__init__.py` | Consumed by Hatchling, CLI `--version`, and release scripts |

## Known quirks

- Dates render `YYYY-MM-DD HH:MM WIB`; HTML bodies are flattened to text (`textutil`).
- `forum` / `announcements` take `--limit`; `thread` returns the whole thread.
- Moodle WS field names vary by version — `api.py` handles the known variants.
- `login` cannot work for accounts behind an external SSO login page.

## Recent history

- v0.1.0 — initial release baseline
- Added pretty CLI output: default table on TTY, JSON when piped, `-f` format flags
- Added `watch` command group: background monitor for any subcommand, git-style unified diff
  of canonical JSON output, webhook notifications.
- v0.2.0 (branch `feat/moodle-ws-api`) — replaced HTML scraping with the Moodle mobile
  web-service API. New commands: `course-detail`, `people`, `grades`, `course-updates`,
  `deadlines`, `calendar`, `notifications`, `assignment-detail`, `submit`. Dropped
  `beautifulsoup4` / `lxml`. `forums` now returns forum *instance* ids.

## `watch` design notes

- State: `~/.config/scele/watches/<name>/` — `watch.json` (config), `state.json`
  (`last_hash` + `last_canonical`), `events.jsonl` (append-only), `daemon.pid`, `daemon.log`.
- Each tick runs `python -m scele -c <command>` as a child process (isolation; reuses all
  auth). Volatile keys (`token`, `token_preview`, `age_days`, legacy `sesskey`) are
  stripped before diffing (`watch._VOLATILE_KEYS`).
- Diff = `difflib.unified_diff`, 3 lines context (git default). Change events carry
  `diff` + `added_lines`/`removed_lines` + full `snapshot`.
- Webhook: plain JSON POST, `--webhook-header` passthrough only (no HMAC), 3 retries w/ backoff.
- **POSIX only** (`os.fork`-style detach via `subprocess` + `start_new_session`). No
  reboot persistence.
- **Ephemeral**: a watch exists only while running. `run_loop` deletes its own dir on
  exit; `watch ls` calls `prune()` to drop watches whose process is gone; `watch clear`
  stops + deletes all. There is no "stopped" retained state and no `rm --keep`.

## Open items

- Windows background support for `watch` (deferred).
- Optional `watch resume --all` after reboot (deferred).
