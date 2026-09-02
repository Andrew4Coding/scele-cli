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
| `api.py` | High-level operations bridging `SceleSession` and parsers |
| `parsers.py` | BeautifulSoup HTML parsers for Moodle pages (defensive extraction) |
| `models.py` | Dataclasses with `to_dict()` for all domain objects |
| `schema.py` | Runtime introspection — generates `scele schema` JSON manifest |
| `output.py` | Smart rendering: ANSI table on TTY, JSON/YAML when piped, `-f`/`-c` flags |
| `auth.py` | Moodle login form scraping, credential handling |
| `session.py` | `SceleSession` HTTP wrapper with auth-redirect interception |
| `config.py` | XDG/APPDATA config dir, `cookies.json` persistence, `watches_dir()` |
| `watch.py` | Background watches: canonicalize + git-style unified-diff of a command's JSON output, append-only event log, webhook delivery, POSIX detach/liveness/stop, `clear()` + `prune()`. A watch is deleted when it stops. State under `~/.config/scele/watches/<name>/` |

## `tests/`

| File | Coverage |
|------|----------|
| `test_parsers.py` | Parser unit tests + schema generator tests. Uses fixtures from `$SCELE_FIXTURES` or companion `scele_cli_recorder` repo. Skips gracefully if absent. |
| `test_watch.py` | `watch` command: canonicalization, unified diff, tick change-detection, webhook delivery + retry, listing/rename/remove, CLI wiring. Stubs `watch.run_command`; no network. |

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
