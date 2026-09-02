---
role: agent-instruction
scope: constraints
description: Constraints, boundaries, and evolution rules
---

# Rules & Constraints

## Output contract (non-negotiable)

- **stdout** must contain exactly one logical JSON document per run.
  - **Sole exception**: a *foreground* `scele watch <cmd>` streams newline-delimited JSON
    events (one `WatchEvent` per line). `watch ls/run/rm/clear/rename/logs` remain single-document.
- Watches are ephemeral: a watch exists only while its process runs. When the loop ends it
  deletes its own directory; `watch ls` prunes any watch whose process is gone; `watch clear`
  stops and deletes every watch.
- **stderr** is for errors only: `{"ok": false, "error": "<code>", "message": "<text>"}`.
  - Error codes: `not_authenticated`, `login_failed`, `request_failed`, `watch_not_found`.
  A Moodle `exception` payload becomes `not_authenticated` for the token-expiry family
  (`session._REAUTH_CODES`) and `request_failed` otherwise.
- **Exit codes**: `0` = success, `1` = any error. No other exit codes.
- Never mix human-readable text into stdout when piped. The `output.py` module handles TTY detection.
- Watch webhook POSTs are outbound network side-effects — configured explicitly by the user
  via `--webhook`; delivery successes/failures are logged as `webhook` events, never to stdout.

## Schema-driven design

- **Never hard-code command lists or parameter schemas.** Always derive from `scele schema`.
- When adding a command, ensure `schema.py` can introspect it automatically.

## Credentials & security

- Credentials are handled via masked prompt (`getpass`) or environment variables (`SCELE_USERNAME`, `SCELE_PASSWORD`).
- The **password is never written to disk**. `auth.py` POSTs it once to `/login/token.php`; only the
  returned web-service token is persisted (`token.json`, `0o600`), and only after it verifies.
- A failed login must leave any existing `token.json` untouched.
- The raw token is never printed — `config.token_status()` exposes only a masked preview.

## Protected files & areas

- `~/.config/scele/token.json` — never modify outside `config.py`
- User credential data — never persist beyond the login request
- `_harness/.setup/` — harness setup templates, do not modify

## Versioning

- `src/scele/__init__.py:__version__` is the **single source of truth** for the project version.
- Do not duplicate version strings elsewhere. Build tools, CLI, and release scripts all read from this one location.

## Defensive mapping

- `api.py` functions must tolerate missing / null web-service fields (`.get(...)`, `or []`,
  `or ""`) — a sparse payload yields empty strings, never an exception.
- Moodle WS field names differ across versions; handle the known variants when it's cheap
  (`posts` vs `messages`, `parentid` vs `parent`, modern vs `_paginated` discussion calls).
- Turn HTML into text with `textutil.clean_html`; turn epochs into strings with `textutil.wib` /
  `textutil.until`. Do not emit raw HTML or bare epoch integers.

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
- Example: adding a new command = at least 3 commits: `feat: add FooBar model`, `feat: map core_foo_get_bar in api`, `feat: add 'foobar' CLI command`.

## Context7

- **Always use Context7 MCP** (`resolve-library-id` → `query-docs`) to fetch current documentation when working with any library, framework, SDK, API, or CLI tool — even well-known ones (Click, Requests, pytest, the Moodle web-service API, etc.).
- Prefer Context7 over web search for library documentation.
- Use even when you think you know the answer — training data may not reflect recent changes.
- **Do not use** Context7 for: refactoring, business logic, code review, or general programming concepts.

## Write operations

- Commands that modify state (`enrol`, `subscribe`, `post`, `reply`, `submit`) must **always** require explicit human confirmation before execution.
- `post`, `reply`, and `submit` require the `--yes` flag to skip the interactive prompt.

## Test conventions

- `test_api.py` drives `api.py` with a `FakeSession` returning canned web-service payloads —
  no network, no token. Every new `api.py` function gets a case here.
- `test_tui_*.py` skip when `textual` is not installed; nothing else needs optional deps.
- Tests never make real HTTP requests.

---

## Harness evolution

| Risk | Action | Rule |
|------|--------|------|
| Low | Update `memory/project.md` | Agent may do freely |
| Medium | Update `routing.md`, `catalog.md`, `workflow.md` | Propose change, wait for approval |
| High | Update `rules.md`, `readme.md` | Propose change, explain rationale, wait for explicit approval |
| Forbidden | Modify `AGENTS.md` entry point, `_harness/.setup/` | Never modify without explicit user request |
