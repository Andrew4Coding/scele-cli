---
role: agent-instruction
scope: workflows
description: Execution flows and procedures
---

# Workflows

## 1. Add a new CLI command

**Trigger**: User asks to add a new command (e.g. `scele grades`).

**Steps**:
1. Find the Moodle web-service function that returns the data (the mobile-app WS allowlist).
   Add the `command → wsfunction` row to `ENDPOINTS.md`.
2. Add a dataclass in `src/scele/models.py` with `to_dict()`.
3. Add a function in `src/scele/api.py`: `s.ws("<wsfunction>", ...)` then map the JSON onto the
   dataclass. Use `textutil.clean_html` for HTML fields and `textutil.wib` / `until` for epochs.
4. Add a test in `tests/test_api.py` — a `FakeSession` with a canned payload + assertions.
5. Add a Click command in `src/scele/cli.py` with proper options, docstring, and error handling.
6. Add `RETURNS` + `EXAMPLES` entries in `src/scele/schema.py`; add a renderer branch in
   `src/scele/output.py` only if the model needs one (flat models render as a table automatically).
7. Run `make test` to verify.
8. Micro-commit each step with conventional commit messages.

**Confirmation needed**: Only if the command modifies state (writes). Read-only commands can proceed without confirmation.

## 1b. Modify the `watch` command

**Trigger**: User asks to change background-watch behavior (diffing, webhooks, daemon, subcommands).

**Steps**:
1. Core logic (canonicalize / unified diff / event log / webhook delivery / daemon
   spawn+liveness+stop) lives in `src/scele/watch.py` — no parser or model changes needed;
   `watch` reuses existing commands via a child `scele -c <cmd>` process.
2. CLI surface is the `watch` group in `src/scele/cli.py` (`_WatchGroup` makes
   `watch <cmd>` an alias for `watch start <cmd>`): `ls`, `run`, `rm`, `clear`, `rename`, `logs`.
   Watches are ephemeral — stopping one deletes it; `ls` prunes dead ones.
3. Update `RETURNS["watch"]` / `EXAMPLES["watch"]` in `src/scele/schema.py` if the
   surface changed (`test_schema_manifest` enforces non-empty entries).
4. Tests: `tests/test_watch.py` (stub `watch.run_command`; never hits the network).
5. Sync docs: `CLAUDE.md` output-contract note, `AGENTS.md.bak`, `skills/scele/SKILL.md`.
   `watch._VOLATILE_KEYS` strips keys that change every run (e.g. `token`) before diffing.
6. Run `make test`. Micro-commit each step.

**Confirmation needed**: No (read-only unless it changes webhook/daemon side-effects).

## 2. Fix a data-mapping bug

**Trigger**: A command returns wrong/missing data.

**Steps**:
1. Check `ENDPOINTS.md` for the web-service function the command calls.
2. Inspect the real payload: `scele -c <cmd> ...` or a one-off `s.ws("<wsfunction>", ...)`.
   Moodle WS field names vary by version — handle both when it's cheap (`posts` vs `messages`).
3. Fix the mapping in `src/scele/api.py` (or a helper in `src/scele/textutil.py`).
4. Update or add a `FakeSession` case in `tests/test_api.py`.
5. Run `make test`.
6. Commit: `fix: <description>`.

**Confirmation needed**: No (read-only code change).

## 3. Modify output formatting

**Trigger**: User wants to change how data is displayed.

**Steps**:
1. Modify `src/scele/output.py`.
2. Ensure the JSON output contract is preserved (stdout = one JSON doc when piped).
3. Test both TTY and piped output.
4. Commit: `feat:` or `fix:` as appropriate.

**Confirmation needed**: No.

## 4. Cut a release

**Trigger**: User says to release a new version.

**Steps**:
1. Confirm the version number with the user.
2. Run `make release VERSION=x.y.z` (bumps version in `__init__.py`, commits, tags).
3. Push: `git push origin main --follow-tags`.
4. CI (`release.yml`) builds binaries and publishes.
5. Verify release on GitHub.

**Confirmation needed**: Yes — always confirm version number before running.

## 5. Debug authentication

**Trigger**: Login fails or session expires unexpectedly.

**Steps**:
1. Run `scele whoami` to check token state + identity.
2. Check `src/scele/auth.py` — the `/login/token.php` request and its verification call.
3. Check `src/scele/session.py` — `_REAUTH_CODES` decides which Moodle errorcodes map to
   `not_authenticated` (re-login) vs `request_failed`.
4. Check `src/scele/config.py` for `token.json` persistence.
5. `{"error":"login_failed"}` with a valid password usually means the account authenticates
   through an external SSO page — `/login/token.php` cannot mint a token for it.

**Confirmation needed**: No (diagnostic). But if a fix changes auth behavior, explain before committing.

---

## Confirmation boundaries

| Action | Confirmation required? |
|--------|----------------------|
| Read-only code changes | No |
| Adding tests | No |
| Documentation updates | No |
| State-modifying commands (post, reply, enrol) | **Yes** |
| File deletions | **Yes** |
| Version bump / release | **Yes** |
| Modifying `rules.md` or `readme.md` | **Yes** |
| Updating `memory/project.md` | No |
