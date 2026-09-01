---
role: agent-instruction
scope: constraints
description: Constraints, boundaries, and evolution rules
---

# Rules & Constraints

## Output contract (non-negotiable)

- **stdout** must contain exactly one logical JSON document per run.
- **stderr** is for errors only: `{"ok": false, "error": "<code>", "message": "<text>"}`.
- **Exit codes**: `0` = success, `1` = any error. No other exit codes.
- Never mix human-readable text into stdout when piped. The `output.py` module handles TTY detection.

## Schema-driven design

- **Never hard-code command lists or parameter schemas.** Always derive from `scele schema`.
- When adding a command, ensure `schema.py` can introspect it automatically.

## Credentials & security

- Credentials are handled via masked prompt (`getpass`) or environment variables (`SCELE_USERNAME`, `SCELE_PASSWORD`).
- Credentials are **never** written to disk. Only session cookies are persisted (`cookies.json` with `0o600` permissions).
- Do not log, print, or expose passwords in any output.

## Protected files & areas

- `~/.config/scele/cookies.json` — never modify outside `config.py`
- User credential data — never persist beyond the login request
- `_harness/.setup/` — harness setup templates, do not modify

## Versioning

- `src/scele/__init__.py:__version__` is the **single source of truth** for the project version.
- Do not duplicate version strings elsewhere. Build tools, CLI, and release scripts all read from this one location.

## Defensive parsing

- All HTML parsers must handle missing DOM elements gracefully (return `None`, `""`, or `[]` — never raise `AttributeError`).
- Use the established helper functions (`_text()`, `_body()`, `_qs()`, `_main()`) in `parsers.py`.

## Micro-commits

- Make **small, atomic commits** — each commit is one logical change.
- Use **conventional commit** messages:
  - `feat:` — new feature or command
  - `fix:` — bug fix
  - `refactor:` — code restructuring without behavior change
  - `test:` — adding or updating tests
  - `docs:` — documentation only
  - `chore:` — build, CI, dependency, or tooling changes
  - `style:` — formatting, whitespace, lint (no logic change)
- Each commit must pass tests (`make test`).
- **Commit frequently** — don't batch unrelated changes into one commit.
- Example: adding a new command = at least 3 commits: `feat: add FooBar model`, `feat: add parser for /foo/bar`, `feat: add 'foobar' CLI command`.

## Context7

- **Always use Context7 MCP** (`resolve-library-id` → `query-docs`) to fetch current documentation when working with any library, framework, SDK, API, or CLI tool — even well-known ones (Click, BeautifulSoup, Requests, pytest, etc.).
- Prefer Context7 over web search for library documentation.
- Use even when you think you know the answer — training data may not reflect recent changes.
- **Do not use** Context7 for: refactoring, business logic, code review, or general programming concepts.

## Write operations

- Commands that modify state (`enrol`, `subscribe`, `post`, `reply`, `download`) must **always** require explicit human confirmation before execution.
- `post` and `reply` require the `--yes` flag to skip the interactive prompt.

## Test conventions

- Parser tests use capture fixtures (via `$SCELE_FIXTURES` or companion recorder repo).
- Tests skip gracefully if fixtures are absent — never fail on missing fixtures.
- All new parsers must have corresponding tests.

---

## Harness evolution

| Risk | Action | Rule |
|------|--------|------|
| Low | Update `memory/project.md` | Agent may do freely |
| Medium | Update `routing.md`, `catalog.md`, `workflow.md` | Propose change, wait for approval |
| High | Update `rules.md`, `readme.md` | Propose change, explain rationale, wait for explicit approval |
| Forbidden | Modify `AGENTS.md` entry point, `_harness/.setup/` | Never modify without explicit user request |
