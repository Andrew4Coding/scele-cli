---
role: agent-instruction
scope: workflows
description: Execution flows and procedures
---

# Workflows

## 1. Add a new CLI command

**Trigger**: User asks to add a new command (e.g. `scele grades`).

**Steps**:
1. Check `ENDPOINTS.md` for the target Moodle URL and DOM structure. If not documented, inspect the page and document it first.
2. Add a dataclass in `src/scele/models.py` with `to_dict()`.
3. Add a parser function in `src/scele/parsers.py` using defensive helpers (`_text()`, `_body()`, etc.).
4. Add a test in `tests/test_parsers.py`.
5. Add an API method in `src/scele/api.py` that calls the session and parser.
6. Add a Click command in `src/scele/cli.py` with proper options, docstring, and error handling.
7. Run `make test` to verify.
8. Micro-commit each step with conventional commit messages.

**Confirmation needed**: Only if the command modifies state (writes). Read-only commands can proceed without confirmation.

## 2. Fix a parser bug

**Trigger**: A command returns wrong/missing data.

**Steps**:
1. Check `ENDPOINTS.md` for the expected URL and DOM structure.
2. If fixtures exist, reproduce with existing test. Otherwise, note the issue.
3. Fix the parser in `src/scele/parsers.py`.
4. Update or add tests in `tests/test_parsers.py`.
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
1. Run `scele whoami` to check current session state.
2. Check `src/scele/auth.py` for login form parsing.
3. Check `src/scele/session.py` for redirect interception.
4. Check `src/scele/config.py` for cookie persistence.
5. If SCELE's login page HTML changed, update `auth.py` parser.

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
