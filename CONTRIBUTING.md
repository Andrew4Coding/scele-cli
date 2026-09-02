# Contributing to scele-cli

Thanks for wanting to help. `scele-cli` is a command-line client for
[SCELE](https://scele.cs.ui.ac.id), the Moodle instance of Fakultas Ilmu Komputer,
Universitas Indonesia.

This document covers how to get set up, how the code is laid out, and the handful of
conventions that keep the tool predictable. If something here is out of date, that is a bug
— [open an issue](https://github.com/Andrew4Coding/scele-cli/issues).

## Getting set up

Requires Python 3.10 or newer.

```bash
git clone https://github.com/Andrew4Coding/scele-cli.git
cd scele-cli
make dev            # python3 -m venv .venv && .venv/bin/pip install -e ".[dev,build]"
make test           # .venv/bin/pytest -q
```

`make dev` gives you an editable install inside `.venv`. To put a `scele` on your `PATH`
that tracks your working tree:

```bash
./install.sh --editable
```

| Target | What it does |
| --- | --- |
| `make dev` | Editable install into `.venv` with the `dev` and `build` extras. |
| `make test` | `pytest -q`. |
| `make binary` | PyInstaller onedir bundle into `dist/scele/` — this OS/arch only, no cross-compile. |
| `make install` | Same as `./install.sh`. |
| `make uninstall` | `./install.sh --uninstall`. |

Optional extras: `yaml` (`-f yaml` output), `tui` (the `scele tui` interface), `build`
(PyInstaller).

## How it works

`scele-cli` drives SCELE through the **official Moodle mobile web-service API**. There is no
HTML scraping, no session cookie, and no `sesskey`. `scele login` exchanges a
username/password for a web-service token via `/login/token.php`, verifies it, and stores
**only the token**. Everything after that is a `POST` to
`/webservice/rest/server.php`.

Keep it that way. A patch that scrapes a page or drives the web UI will not be merged —
if the data you need has no web-service function, say so in an issue and we will work out
what to do.

## Layout

```
src/scele/
  cli.py        click command surface; _guard() turns any exception into a JSON error,
                _out() prints via output.emit
  api.py        one function per command: calls web-service functions, maps JSON onto models
  session.py    SceleSession — holds the token + base URL, ws(wsfunction, **params),
                flattens nested params to Moodle's key[0][sub] form, raises
                RequestFailedError / NotAuthenticatedError
  auth.py       terminal_login: mint, verify, store a token
  models.py     dataclasses with to_dict()
  output.py     emit() — one document to stdout; fail() — JSON error to stderr, exit 1
  textutil.py   clean_html(), wib()/until() — epoch to WIB strings and countdowns
  config.py     config dir + token store
  schema.py     builds the `scele schema` manifest by introspecting the click group
  watch.py      background watches: re-run a subcommand, diff its output, POST to webhooks
  tui/          the optional Textual interface
tests/          pytest, no network — see below
website/        the documentation site (Zensical); see website/README.md
```

`ENDPOINTS.md` maps every command to the web-service function(s) behind it.

## The output contract

This is the part most likely to break something downstream, so treat it as an API.

- Every command prints **exactly one JSON document to stdout** via `output.emit` — rendered
  as a table on a terminal, plain JSON when piped.
- Errors print `{"ok": false, "error": <code>, "message": ...}` to **stderr** via
  `output.fail`, and exit `1`. Codes: `not_authenticated`, `login_failed`,
  `request_failed`, `watch_not_found`.
- Prompts and notices go to stderr, **never** stdout.
- `-c` / `--compact` (before the subcommand) gives single-line JSON.

Three deliberate exceptions: `scele schema` always prints JSON even on a terminal; a
foreground `scele watch <cmd>` streams newline-delimited JSON events; `scele tui` prints no
document at all.

## Adding or changing a command

1. **`api.py`** — add one function. It takes a `SceleSession`, makes one or more
   `s.ws("<wsfunction>", ...)` calls, and maps the result onto a dataclass in `models.py`.
   Pass nested parameters as plain dicts/lists; `session._flatten` renders `key[0][sub]`
   for you.
2. **`cli.py`** — add the click command. Wrap the call in `_guard(...)` and print with
   `_out(ctx, ...)`. The docstring becomes the command's summary everywhere, so write it as
   one clear sentence.
3. **`schema.py`** — add an entry to `RETURNS` and to `EXAMPLES`.
   `tests/test_schema.py` fails if either is missing.
4. **`ENDPOINTS.md`** — list the web-service function(s) the command calls.
5. **Docs** — update `README.md`, `skills/scele/SKILL.md`, and the site: add a page under
   `website/docs/commands/<group>/<name>.md` and an entry in the `nav` in
   `website/zensical.toml`.
6. **Tests** — add a case to `tests/`.

### Write commands

Anything that changes state on SCELE — `enrol`, `subscribe`, `post`, `reply`, `submit`,
`quiz-start`, `quiz-answer --finish` — must require `--yes` or an interactive confirmation.
The irreversible ones (`quiz-start` consumes an attempt, `quiz-answer --finish` submits for
grading, `submit` hands work to a teacher) require `--yes` with no way around it. Do not
relax this.

### Credentials

The password is used for exactly one request and is **never written to disk** — not to the
token file, not to a log, not to an error message. There is deliberately no `--password`
flag, because arguments are visible to other processes and land in shell history. Read
credentials from the prompt or from `SCELE_USERNAME` / `SCELE_PASSWORD`.

Never commit a token, a real username, or a real course/user id from your own account.

## Tests

```bash
make test
# or: .venv/bin/pytest -q tests/test_api.py
```

Tests **do not touch the network**. `tests/test_api.py` drives `api.py` through a
`FakeSession` that returns canned JSON per `wsfunction` and records the calls made, so a
test asserts both the mapping and which web-service functions were called. Copy that
pattern for new commands — trim a real payload down to the fields the code reads, and
redact anything identifying.

`tests/test_schema.py` enforces that the `scele schema` manifest stays complete.

## Style

- Match the surrounding code. The codebase is plain, dependency-light Python: runtime
  dependencies are just `requests` and `click`.
- One-line docstring above a function saying what it does. No inline commentary on
  individual lines, loops, or assignments.
- Type hints on function signatures.
- Dataclasses in `models.py` carry a `to_dict()`.

## Commits and pull requests

Commit messages follow Conventional Commits, with an optional scope:

```
feat: add depth in the forum replies
fix(packaging): bundle the TUI stylesheet in the binary
docs: update npm package references to scele-cli
perf(packaging): ship the binary as a --onedir bundle
chore: restore CI + release workflows
```

Common types: `feat`, `fix`, `docs`, `perf`, `refactor`, `test`, `chore`.

Before opening a PR:

- [ ] `make test` is green
- [ ] `scele schema` runs and includes your command
- [ ] `README.md`, `skills/scele/SKILL.md`, `ENDPOINTS.md` and the website reflect the change
- [ ] No credentials, tokens, or personal SCELE data in the diff

Describe what changed and why, and paste the output of any command you added. Small,
focused PRs get reviewed faster than large ones.

## Documentation site

The site under `website/` is built with [Zensical](https://zensical.org/):

```bash
cd website
python3 -m venv .venv && .venv/bin/pip install zensical
.venv/bin/zensical serve      # http://localhost:8000
.venv/bin/zensical build      # -> website/site/
```

`zensical build` validates internal links and reports `No issues found` when clean. See
[website/README.md](website/README.md) for the structure and theming notes.

## Releasing

Maintainers only — see [RELEASING.md](RELEASING.md). In short: `__version__` in
`src/scele/__init__.py` is the single version source, bumped only through
`scripts/release.sh <version>`, and pushing the `v*` tag builds and publishes the release.

## Reporting bugs

Use the [issue form on the docs site](https://andrew4coding.github.io/scele-cli/report/) or
open one [directly on GitHub](https://github.com/Andrew4Coding/scele-cli/issues/new).
Helpful reports include:

- the exact command you ran, with ids and credentials redacted
- the full error object from stderr
- `scele --version` and your OS
- whether `scele whoami` reports `authenticated: true` at the time

**Never paste your token.** It lives in `~/.config/scele/token.json` and it is a
credential.

## License

By contributing you agree that your contributions are licensed under the
[MIT License](LICENSE.md).
