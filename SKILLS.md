# scele as an Agent Skill

`skills/scele/SKILL.md` is a portable [Agent Skill](https://docs.claude.com/en/docs/claude-code/skills)
that teaches an AI agent how to drive the `scele` CLI — discovering commands via `scele schema`,
the auth flow, the course→forum→thread ID chain, and the JSON output contract.

The skill and the CLI install separately:

| | what it is | install |
|---|---|---|
| **CLI** | the `scele` command | `curl -fsSL https://raw.githubusercontent.com/Andrew4Coding/scele-cli/main/install-bin.sh \| sh` (binary, no Python) — or `pipx install git+https://github.com/Andrew4Coding/scele-cli.git` |
| **Skill** | instructions telling an agent *when and how* to call `scele` | `npm install -g scele-cli` or `npx skills add Andrew4Coding/scele-cli` |

## Install the skill — `npx skills`

Uses the [`skills`](https://github.com/vercel-labs/skills) CLI (a package manager for Agent Skills):

```bash
npx skills add Andrew4Coding/scele-cli          # interactive: pick scope + agents
npx skills add Andrew4Coding/scele-cli -g -y     # global, no prompts
npx skills add Andrew4Coding/scele-cli --list    # just show what's in the repo
npx skills remove scele
npx skills update scele
```

It clones the repo, finds `skills/scele/SKILL.md`, and links it into your agent's skills
directory (`~/.claude/skills/` global, or `./.claude/skills/` in a project).

## Install the skill — bundled installer (`npm` / `npx`)

Install globally via npm so `scele-cli` is added to your `PATH`:

```bash
npm install -g scele-cli

scele-cli                   # -> ~/.claude/skills/scele/   (user scope)
scele-cli --project         # -> ./.claude/skills/scele/   (repo scope)
scele-cli --dir <path>      # -> <path>/scele/
scele-cli --with-cli        # also installs the scele Python CLI
scele-cli --uninstall       # remove the installed skill
```

Or run on-demand with `npx` without a global install:

```bash
npx scele-cli                   # -> ~/.claude/skills/scele/
npx scele-cli --project         # -> ./.claude/skills/scele/
npx scele-cli --with-cli        # also installs the scele CLI
npx scele-cli --uninstall
```

## Manual install (no npx)

```bash
mkdir -p ~/.claude/skills
cp -r skills/scele ~/.claude/skills/
```

Locations: Claude Code user `~/.claude/skills/scele/`, project `<repo>/.claude/skills/scele/`.

## Verify

```bash
scele --version              # CLI present
npx skills ls                # skill listed
```

Then ask your agent *"list my scele courses"* — it should run `scele whoami` then `scele courses`.

## Keeping it current

Re-run `npx skills update scele` (or the `npx scele-skill` command). Keep
`skills/scele/SKILL.md` in sync with `AGENTS.md.bak`, `src/scele/schema.py`, and
`scele schema` when commands change.
