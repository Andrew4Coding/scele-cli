#!/usr/bin/env node
/**
 * Install the `scele` agent skill into an agent's skills directory.
 *
 *   scele skill                 -> ~/.claude/skills/scele/        (user scope)
 *   scele skill --project       -> ./.claude/skills/scele/        (repo scope)
 *   scele skill --dir <path>    -> <path>/scele/
 *   scele skill --uninstall     -> remove the installed skill
 *
 * Zero dependencies. Node >= 16.
 */
import { cpSync, existsSync, mkdirSync, rmSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PKG_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const SKILL_SRC = join(PKG_ROOT, "skills", "scele");
const SKILL_NAME = "scele";

function parseArgs(argv) {
  const o = { project: false, uninstall: false, dir: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--project" || a === "-p") o.project = true;
    else if (a === "--uninstall") o.uninstall = true;
    else if (a === "--dir") o.dir = argv[++i];
    else if (a === "-h" || a === "--help") {
      console.log(readHelp());
      process.exit(0);
    } else {
      console.error(`unknown option: ${a}`);
      process.exit(2);
    }
  }
  return o;
}

function readHelp() {
  return `Usage: scele skill [OPTIONS]

Install the \`scele\` agent skill into an AI agent's skills directory.

Options:
  --project, -p       Install to repo scope (./.claude/skills/scele/)
  --dir <path>        Install to custom directory (<path>/scele/)
  --uninstall         Remove the installed skill
  -h, --help          Show this message

Examples:
  scele skill                 # -> ~/.claude/skills/scele/ (user scope)
  scele skill --project       # -> ./.claude/skills/scele/ (repo scope)
  scele skill --uninstall     # remove installed skill`;
}

function skillsBaseDir(opts) {
  if (opts.dir) return resolve(opts.dir);
  if (opts.project) return resolve(process.cwd(), ".claude", "skills");
  return join(homedir(), ".claude", "skills");
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  const dest = join(skillsBaseDir(opts), SKILL_NAME);

  if (opts.uninstall) {
    rmSync(dest, { recursive: true, force: true });
    console.log(`Removed ${dest}`);
    return;
  }

  if (!existsSync(join(SKILL_SRC, "SKILL.md"))) {
    console.error(`skill source missing at ${SKILL_SRC}`);
    process.exit(1);
  }

  mkdirSync(dirname(dest), { recursive: true });
  rmSync(dest, { recursive: true, force: true });
  cpSync(SKILL_SRC, dest, { recursive: true });
  console.log(`Installed skill -> ${dest}`);

  console.log("\nNext:");
  console.log("  - Restart your agent / Claude Code so it picks up the skill.");
  console.log("  - Then:  scele login   &&   scele courses");
}

main();
