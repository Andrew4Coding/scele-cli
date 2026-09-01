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
| Stateless CLI (no background daemon) | Each invocation loads cookies, runs, outputs, exits — minimal footprint |
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

## Open items

- (none yet)
