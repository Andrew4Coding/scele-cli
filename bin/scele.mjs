#!/usr/bin/env node
/**
 * scele CLI runner
 *
 * Dispatches to either:
 * 1. The standalone prebuilt binary (if installed at ~/.local/lib/scele-app/scele)
 * 2. System Python (using bundled src/scele with requests + click)
 * 3. Bootstraps the prebuilt binary automatically if neither is ready.
 */
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { homedir, platform } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const PKG_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const SRC_DIR = join(PKG_ROOT, "src");

function findWorkingPython() {
  for (const py of ["python3", "python"]) {
    try {
      const res = spawnSync(py, ["-c", "import requests, click"], { stdio: "ignore" });
      if (res.status === 0) return py;
    } catch {
      // not available
    }
  }
  return null;
}

function getPrebuiltBinaryPath() {
  const isWin = platform() === "win32";
  if (isWin) {
    const localAppData = process.env.LOCALAPPDATA || join(homedir(), "AppData", "Local");
    return join(localAppData, "Programs", "scele", "scele.exe");
  }
  return join(homedir(), ".local", "lib", "scele-app", "scele");
}

function bootstrapBinary() {
  const isWin = platform() === "win32";
  const script = isWin ? join(PKG_ROOT, "install-bin.ps1") : join(PKG_ROOT, "install-bin.sh");
  if (!existsSync(script)) return null;

  console.error("Bootstrapping prebuilt scele binary...");
  const cmd = isWin
    ? ["powershell", ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script]]
    : ["sh", [script]];
  spawnSync(cmd[0], cmd[1], { stdio: "inherit", cwd: PKG_ROOT });
  const bin = getPrebuiltBinaryPath();
  return existsSync(bin) ? bin : null;
}

function main() {
  const args = process.argv.slice(2);

  // Allow installing the agent skill via flag: scele --install-skill
  if (args[0] === "--install-skill" || args[0] === "--skill") {
    const skillScript = join(PKG_ROOT, "bin", "install-skill.mjs");
    const r = spawnSync(process.execPath, [skillScript, ...args.slice(1)], { stdio: "inherit" });
    process.exit(r.status ?? 0);
  }

  // 1. Prefer prebuilt binary if already installed
  const prebuilt = getPrebuiltBinaryPath();
  if (existsSync(prebuilt)) {
    const r = spawnSync(prebuilt, args, { stdio: "inherit" });
    process.exit(r.status ?? 0);
  }

  // 2. Use system python with bundled src/
  const py = findWorkingPython();
  if (py) {
    const env = { ...process.env, PYTHONPATH: SRC_DIR };
    const r = spawnSync(py, ["-m", "scele", ...args], { stdio: "inherit", env });
    process.exit(r.status ?? 0);
  }

  // 3. Fallback: bootstrap prebuilt binary
  const bootstrapped = bootstrapBinary();
  if (bootstrapped && existsSync(bootstrapped)) {
    const r = spawnSync(bootstrapped, args, { stdio: "inherit" });
    process.exit(r.status ?? 0);
  }

  console.error("Error: Could not find Python >=3.10 (with requests and click) or download prebuilt binary.");
  console.error("Install Python 3.10+ or run: curl -fsSL https://raw.githubusercontent.com/Andrew4Coding/scele-cli/main/install-bin.sh | sh");
  process.exit(1);
}

main();
