# scele as an Agent Skill

`skills/scele/SKILL.md` is a portable [Agent Skill](https://docs.claude.com/en/docs/claude-code/skills)
that teaches an AI agent (Claude Code, or anything that reads `SKILL.md` files) how to drive the
`scele` CLI — discovering commands via `scele schema`, the auth flow, the course→forum→thread ID
chain, and the JSON output contract.

The skill and the CLI are separate installs:

| | what it is | install |
|---|---|---|
| **CLI** | the `scele` command (Python) | `./install.sh` / `.\install.ps1` |
| **Skill** | instructions that tell an agent *when and how* to call `scele` | `npx scele-skill` |

## Install the skill

```bash
npx scele-skill                 # -> ~/.claude/skills/scele/     (all your projects)
npx scele-skill --project       # -> ./.claude/skills/scele/     (this repo only)
npx scele-skill --dir <path>    # -> <path>/scele/               (any other agent)
npx scele-skill --with-cli      # also runs the CLI installer
npx scele-skill --uninstall
```

Until this package is published to npm, point `npx` at the source:

```bash
npx github:<you>/scele_cli --with-cli      # from a git remote
npx /path/to/scele_cli --with-cli          # from a local checkout
```

Then restart your agent so it re-scans the skills directory.

## Manual install (no npx)

Copy the folder into any skills directory the agent scans:

```bash
mkdir -p ~/.claude/skills
cp -r skills/scele ~/.claude/skills/
```

Locations by agent:

- Claude Code (user): `~/.claude/skills/scele/`
- Claude Code (project): `<repo>/.claude/skills/scele/`
- Other agents: wherever they load `SKILL.md` bundles from.

## Verify

```bash
scele --version          # CLI present
ls ~/.claude/skills/scele # skill present
```

In Claude Code, ask something like *"list my scele courses"* — it should invoke the skill,
check `scele whoami`, and run `scele courses`.

## Updating

Re-run the same `npx scele-skill …` command; it overwrites the installed copy. Keep
`skills/scele/SKILL.md` in sync with `AGENTS.md` and the `scele schema` output when commands change.
