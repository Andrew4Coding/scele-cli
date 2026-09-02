#!/usr/bin/env node
/**
 * Install the `scele` agent skill into an agent's skills directory.
 *
 *   npx scele-skill                 -> ~/.claude/skills/scele/        (user scope)
 *   npx scele-skill --project       -> ./.claude/skills/scele/        (repo scope)
 *   npx scele-skill --dir <path>    -> <path>/scele/
 *   npx scele-skill --with-cli      -> also install the `scele` Python CLI
 *   npx scele-skill --uninstall     -> remove the installed skill
 *
 * Zero dependencies. Node >= 16.
 */
import { spawnSync } from "node:child_process";
import { cpSync, existsSync, mkdirSync, rmSync } from "node:fs";
import { homedir, platform } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PKG_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const SKILL_SRC = join(PKG_ROOT, "skills", "scele");
const SKILL_NAME = "scele";

function parseArgs(argv) {
  const o = { project: false, withCli: false, uninstall: false, dir: null };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--project" || a === "-p") o.project = true;
    else if (a === "--with-cli") o.withCli = true;
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
  return `scele-cli: installer for the scele agent skill and CLI.

Usage:
  npm install -g scele-cli        install globally (recommended for CLI)
  scele-cli                       install the agent skill (~/.claude/skills/scele/)
  scele-cli --project             install the skill to current repo (./.claude/skills/)
  scele-cli --dir <path>          install the skill to custom directory
  scele-cli --with-cli            also install the scele CLI
  scele-cli --uninstall           remove the installed skill
  scele-cli <command> [args...]   run the scele CLI (e.g. scele-cli courses)

Or on-demand via npx:
  npx scele-cli [--with-cli|--project|--uninstall]`;
}

function skillsBaseDir(opts) {
  if (opts.dir) return resolve(opts.dir);
  if (opts.project) return resolve(process.cwd(), ".claude", "skills");
  return join(homedir(), ".claude", "skills");
}

function runScele(args) {
  const r = spawnSync("scele", args, { stdio: "inherit" });
  if (r.error && r.error.code === "ENOENT") {
    console.error("Error: 'scele' CLI executable was not found on your PATH.");
    console.error("To install it, run:  scele-cli --with-cli");
    console.error("Or install via binary:  curl -fsSL https://raw.githubusercontent.com/Andrew4Coding/scele-cli/main/install-bin.sh | sh");
    process.exit(1);
  }
  process.exit(r.status ?? 0);
}

function installCli() {
  const isWin = platform() === "win32";
  const script = isWin ? join(PKG_ROOT, "install.ps1") : join(PKG_ROOT, "install.sh");
  if (!existsSync(script)) {
    console.error(`CLI installer not found at ${script}; run it from the repo instead.`);
    return 1;
  }
  console.log(`\nInstalling the scele CLI via ${isWin ? "install.ps1" : "install.sh"} ...`);
  const cmd = isWin
    ? ["powershell", ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script]]
    : ["sh", [script]];
  let r = spawnSync(cmd[0], cmd[1], { stdio: "inherit", cwd: PKG_ROOT });
  if (r.status !== 0) {
    const binScript = isWin ? join(PKG_ROOT, "install-bin.ps1") : join(PKG_ROOT, "install-bin.sh");
    if (existsSync(binScript)) {
      console.log(`\nPython install failed. Falling back to prebuilt binary installer (${isWin ? "install-bin.ps1" : "install-bin.sh"}) ...`);
      const binCmd = isWin
        ? ["powershell", ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", binScript]]
        : ["sh", [binScript]];
      r = spawnSync(binCmd[0], binCmd[1], { stdio: "inherit", cwd: PKG_ROOT });
    }
  }
  return r.status ?? 1;
}

function main() {
  const argv = process.argv.slice(2);
  if (argv.length > 0 && !argv[0].startsWith("-")) {
    runScele(argv);
    return;
  }

  const opts = parseArgs(argv);
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

  let cliCode = 0;
  if (opts.withCli) cliCode = installCli();

  console.log("\nNext:");
  console.log("  - Restart your agent / Claude Code so it picks up the skill.");
  if (!opts.withCli) {
    console.log("  - Install the CLI:  scele-cli --with-cli   (or npx scele-cli --with-cli)");
  }
  console.log("  - Then:  scele login   &&   scele courses");
  process.exit(cliCode);
}

main();
