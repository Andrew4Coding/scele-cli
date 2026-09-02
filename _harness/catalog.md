---
role: agent-instruction
scope: structure-lookup
description: Project structure and module lookup
---

# Project Catalog

## Top-level layout

```
SceleCLI/
├── src/scele/          # Core Python package (all source lives here)
├── tests/              # pytest test suite
├── skills/scele/       # Agent Skill manifest (SKILL.md)
├── scripts/            # Build & release automation
├── packaging/          # PyInstaller config
├── bin/                # Node.js skill installer
├── .github/workflows/  # CI/CD (test matrix + release pipeline)
├── AGENTS.md           # Harness entry point
├── CLAUDE.md           # Claude Code guidance
├── ENDPOINTS.md        # Moodle URL & DOM reverse-engineering reference
├── RELEASING.md        # Release checklist
├── SKILLS.md           # Agent Skill installation guide
├── Makefile            # Developer shortcuts
├── pyproject.toml      # Hatchling project config, dependencies, extras
├── package.json        # npm packaging for scele-skill
├── install.sh / .ps1   # Source installers (pipx)
└── install-bin.sh/.ps1 # Prebuilt binary installers
```

## `src/scele/` — Core modules

| Module | Purpose |
|--------|---------|
| `__init__.py` | Single-source version (`__version__`), `BASE_URL` constant |
| `__main__.py` | `python -m scele` entry point |
| `cli.py` | Click command tree: all commands, options, error wrapping, output dispatch |
| `api.py` | One function per command — calls web-service functions via `SceleSession`, maps JSON onto `models.py` |
| `textutil.py` | `clean_html` (Moodle HTML → text), `wib` / `until` (epoch → WIB string / countdown) |
| `models.py` | Dataclasses with `to_dict()` for all domain objects |
| `schema.py` | Runtime introspection — generates `scele schema` JSON manifest |
| `output.py` | Smart rendering: ANSI table on TTY, JSON/YAML when piped, `-f`/`-c` flags |
| `auth.py` | Mint + verify + store a Moodle web-service token from a username/password |
| `session.py` | `SceleSession` — token holder, `ws(wsfunction, **params)` caller, param flattening, `pluginfile_url()` |
| `config.py` | XDG/APPDATA config dir, `token.json` persistence (token only, never the password), `watches_dir()` |
| `watch.py` | Background watches: canonicalize + git-style unified-diff of a command's JSON output, append-only event log, webhook delivery, POSIX detach/liveness/stop, `clear()` + `prune()`. A watch is deleted when it stops. State under `~/.config/scele/watches/<name>/` |

### `src/scele/tui/` — interactive terminal UI (`scele tui`, needs the `[tui]` extra)

Textual app; every screen calls the same `api.*` functions as the CLI in a worker thread.
`app.py` (auth gate + themes + vim keys), `screens/` (one file per view — `dashboard`,
`course`, `forum`, `thread`, `assignment`, `announcements`, `lists` = deadlines/calendar/
notifications/grades/people, `course_info`, `quiz`, `submit`, `composer`, `download`,
`login`, `settings`), `widgets/` (`data_screen.TableScreen` base for the list screens,
`search` filter mixin, `post_view`, `activity_tree`, `course_list`).

## `tests/`

| File | Coverage |
|------|----------|
| `test_api.py` | `api.py` mapping logic against canned web-service payloads via a `FakeSession`. No network, no token. |
| `test_schema.py` | The `scele schema` manifest stays complete; every command has a `RETURNS` + `EXAMPLES` entry. |
| `test_download.py` | `api.download` streaming + progress + pluginfile-URL rewriting. |
| `test_watch.py` | `watch` command: canonicalization, unified diff, tick change-detection, webhook delivery + retry, listing/rename/remove, CLI wiring. Stubs `watch.run_command`; no network. |
| `test_tui_*.py` | Textual UI screens (skip if `textual` is not installed). |

## `skills/scele/`

| File | Purpose |
|------|---------|
| `SKILL.md` | Portable Agent Skill manifest for Claude Code / generic agent consumption |

## `.github/workflows/`

| File | Purpose |
|------|---------|
| `ci.yml` | Matrix test: Ubuntu/macOS/Windows × Python 3.10/3.13 |
| `release.yml` | Multi-arch binary build (5 targets) + wheel/sdist release on tag push |

## `scripts/`

| File | Purpose |
|------|---------|
| `build-binary.sh` | Local PyInstaller standalone build |
| `release.sh` | Version bump → commit → git tag automation |

## `packaging/`

| File | Purpose |
|------|---------|
| `entry.py` | PyInstaller bootstrapper |
| `scele.spec` | PyInstaller one-file build spec |
