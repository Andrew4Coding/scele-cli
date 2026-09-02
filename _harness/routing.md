---
role: agent-instruction
scope: task-routing
description: Task-to-file mapping
---

# Task Routing

Use this file to quickly find which files to read or modify for a given task.

## Code changes

| Task | Primary files | Also check |
|------|--------------|------------|
| Add/modify a CLI command | `src/scele/cli.py` | `src/scele/api.py`, `src/scele/models.py`, `src/scele/schema.py` |
| Modify the `watch` command | `src/scele/watch.py` | `src/scele/cli.py`, `src/scele/schema.py`, `tests/test_watch.py` |
| Map a new web-service function | `src/scele/api.py` | `tests/test_api.py`, `ENDPOINTS.md` |
| Shape HTML / timestamps | `src/scele/textutil.py` | `src/scele/api.py` |
| Change data models | `src/scele/models.py` | `src/scele/schema.py`, `src/scele/output.py` |
| Fix auth / token issues | `src/scele/auth.py`, `src/scele/session.py` | `src/scele/config.py` |
| Change output formatting | `src/scele/output.py` | `src/scele/cli.py` |
| Fix schema introspection | `src/scele/schema.py` | `src/scele/models.py`, `src/scele/cli.py` |
| Update version | `src/scele/__init__.py` | `scripts/release.sh` |

## Tests

| Task | Files |
|------|-------|
| Add/fix api mapping tests | `tests/test_api.py` |
| Add/fix schema tests | `tests/test_schema.py` |
| Add/fix watch tests | `tests/test_watch.py` |
| Run tests | `make test` or `.venv/bin/pytest -q` |

## CI/CD & release

| Task | Files |
|------|-------|
| CI pipeline | `.github/workflows/ci.yml` |
| Release pipeline | `.github/workflows/release.yml` |
| Cut a release | `scripts/release.sh`, `RELEASING.md` |
| Binary build | `packaging/entry.py`, `packaging/scele.spec`, `scripts/build-binary.sh` |

## Documentation

| Task | Files |
|------|-------|
| User-facing README | `README.md` |
| Moodle URL reference | `ENDPOINTS.md` |
| Release checklist | `RELEASING.md` |
| Agent Skill docs | `SKILLS.md`, `skills/scele/SKILL.md` |
| Harness docs | `_harness/*.md` |

## Distribution & packaging

| Task | Files |
|------|-------|
| Python package config | `pyproject.toml` |
| npm / skill packaging | `package.json`, `bin/install-skill.mjs` |
| Source installers | `install.sh`, `install.ps1` |
| Binary installers | `install-bin.sh`, `install-bin.ps1` |

## Common multi-file flows

**Changing `watch`** (diffing, webhooks, daemon, subcommands):
1. `src/scele/watch.py` — core logic (no parser/model changes; reuses existing commands)
2. `src/scele/cli.py` — the `watch` group / `_WatchGroup` alias behavior
3. `src/scele/schema.py` — `RETURNS["watch"]` / `EXAMPLES["watch"]`
4. `tests/test_watch.py`
5. Docs: `CLAUDE.md`, `AGENTS.md.bak`, `skills/scele/SKILL.md`

**Adding a new command** (e.g. `scele grades <course-id>`):
1. `ENDPOINTS.md` — add the row: command → web-service function(s)
2. `src/scele/models.py` — add a dataclass (with `to_dict()`)
3. `src/scele/api.py` — add the function: `s.ws("<wsfunction>", ...)` + map to the dataclass
4. `tests/test_api.py` — add a `FakeSession` payload + assertions
5. `src/scele/cli.py` — add the Click command
6. `src/scele/schema.py` — `RETURNS` + `EXAMPLES` entries; `src/scele/output.py` if it needs a renderer
7. Docs: `README.md`, `skills/scele/SKILL.md`, `AGENTS.md.bak`
8. Micro-commit each step
