# scele-cli

Command-line client for **SCELE** (`https://scele.cs.ui.ac.id`), the Moodle instance of
Fakultas Ilmu Komputer, Universitas Indonesia.

You log in once from the terminal (username + password — SCELE has no CAPTCHA), it saves the
session cookie, and then talks to SCELE over plain HTTP, parsing the same pages you would read
in the browser. Your password is sent only to SCELE, over HTTPS, and never written to disk.

## Install

### Prebuilt binary — no Python needed (recommended)

**Linux / macOS**

```bash
curl -fsSL https://raw.githubusercontent.com/Andrew4Coding/scele-cli/main/install-bin.sh | sh
```

**Windows** (PowerShell)

```powershell
irm https://raw.githubusercontent.com/Andrew4Coding/scele-cli/main/install-bin.ps1 | iex
```

Fetches the latest release binary for your OS/arch, verifies its SHA-256, and drops `scele`
on your `PATH`. Pin a version with `SCELE_VERSION=v0.1.0`, change the location with
`SCELE_BIN_DIR`. Or grab `scele-<os>-<arch>` straight from the
[Releases page](https://github.com/Andrew4Coding/scele-cli/releases) and `chmod +x` it.

Then open a new terminal:

```bash
scele login
scele courses
```

### With Python (pipx)

```bash
pipx install git+https://github.com/Andrew4Coding/scele-cli.git
```

Or from a clone — the scripts bootstrap pip + pipx for you:

```bash
git clone https://github.com/Andrew4Coding/scele-cli.git && cd scele-cli
./install.sh            # Linux / macOS / WSL / Git-Bash   (flags: --editable, --from, --uninstall)
.\install.ps1           # Windows PowerShell
```

### As an agent skill

```bash
npx skills add Andrew4Coding/scele-cli     # installs skills/scele/SKILL.md for your agent
```

See [SKILLS.md](SKILLS.md) and [RELEASING.md](RELEASING.md).

### Shell completion (optional)

```bash
# bash: ~/.bashrc   zsh: ~/.zshrc   (use bash_source / zsh_source accordingly)
echo 'eval "$(_SCELE_COMPLETE=zsh_source scele)"' >> ~/.zshrc
```

```powershell
# PowerShell profile
$env:_SCELE_COMPLETE = 'powershell_source'; scele | Out-String | Invoke-Expression
```

## Output

Every command prints exactly **one JSON document to stdout** — a list, an object, or for
actions `{"ok": true, "action": "...", ...}`. Errors print `{"ok": false, "error": "...",
"message": "..."}` to **stderr** and exit non-zero. Add `-c` / `--compact` (before the
subcommand) for single-line JSON. There is no human-formatted mode.

`scele schema` prints a machine-readable manifest of every command, its arguments, and its
return shape — the entry point for scripts and AI agents. See [AGENTS.md](AGENTS.md).

```bash
scele courses | jq '.[].id'
scele -c assignment 222043 | jq .fields
```

## Usage

```bash
scele login                       # prompts: SCELE username + password (hidden)
scele whoami

scele courses                     # your dashboard courses
scele categories [--id 31]        # browse the catalog
scele category 31                 # courses in a category
scele course 4234                 # section / activity outline

scele forums 4234                 # forums in a course
scele forum 221050                # discussions in a forum
scele thread 62493                # posts in a discussion
scele post 17474 --subject "..." --message "..."
scele reply 553756 --message "..."
scele subscribe 17474 [--discussion 62493]

scele assignments 4234
scele assignment 222043           # submission status + files

scele resources 4234
scele download 222038 -o ./dl     # by resource cmid
scele download /pluginfile.php/... -o ./dl

scele announcements
```

## Config

- Session cookie:
  - Linux/macOS: `$XDG_CONFIG_HOME/scele/` or `~/.config/scele/cookies.json`
  - Windows: `%APPDATA%\scele\cookies.json`
  - override with `SCELE_CONFIG_DIR`
- `SCELE_BASE_URL` — point at a different Moodle.
- `SCELE_USERNAME` / `SCELE_PASSWORD` — non-interactive `scele login`.

## Layout

```
src/scele/
  cli.py        click command surface
  api.py        high-level operations (one function per command)
  session.py    authenticated requests.Session + login-redirect detection
  auth.py       terminal username/password login
  parsers.py    BeautifulSoup parsers, one per page type
  models.py     dataclasses
  output.py     JSON rendering
  config.py     config-dir + cookie store
  schema.py     `scele schema` manifest
```

See `ENDPOINTS.md` for the underlying Moodle endpoints and page structure,
`AGENTS.md` for using `scele` programmatically, and `SKILLS.md` for installing the
`scele` **Agent Skill** (`npx skills add Andrew4Coding/scele-cli`) so agents know how to use it.

The page-capture tooling used to reverse-engineer SCELE's HTML lives in the sibling
`../scele_cli_recorder/` and is not needed to run the CLI.
