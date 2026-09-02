# Releasing

## Cut a release

```bash
chmod +x scripts/*.sh          # first time
scripts/release.sh 0.2.0       # bumps src/scele/__init__.py, commits, tags v0.2.0
git push origin main --follow-tags
```

Pushing the `v*` tag triggers `.github/workflows/release.yml`, which:

1. builds the `scele` **onedir bundle** on 5 runners
   (`linux-x86_64`, `linux-aarch64`, `macos-x86_64`, `macos-arm64`, `windows-x86_64`),
2. packs each `dist/scele/` as `scele-<target>.tar.gz` (`.zip` on Windows),
3. builds the Python `sdist` + `wheel`,
4. creates the GitHub Release with every archive, `checksums.txt`, and auto-generated notes.

You can also re-run it for an existing tag from the Actions tab
(**Release → Run workflow → tag**).

> The bundle is **onedir**, not onefile: a onefile binary re-extracts its whole
> archive to a temp dir on every run (multiple seconds); onedir starts in ~0.1s.
> `install-bin.sh` / `install-bin.ps1` unpack the archive to
> `~/.local/lib/scele-app` (or `%LOCALAPPDATA%\Programs\scele`) and link
> `scele` onto `PATH`.
>
> If you restore `release.yml` from history, its **Package** step still `cp`s a
> single file — change it to tar/zip `dist/scele/` and name the asset
> `scele-<target>.tar.gz` / `.zip`.

## Version source

`src/scele/__init__.py` `__version__` is the single source. `pyproject.toml` reads it via
`[tool.hatch.version]`; `scele schema` and `scele --version` report it.

## Build a binary locally

```bash
pip install -e ".[build]"        # add ".[build,tui]" to bundle the `scele tui` UI
scripts/build-binary.sh          # -> dist/scele/  (this OS/arch only; no cross-compile)
tar -czf scele-macos-arm64.tar.gz -C dist scele   # what the workflow ships
```

## What users run

| method | command | needs |
|---|---|---|
| binary (raw script) | `curl -fsSL https://raw.githubusercontent.com/Andrew4Coding/scele-cli/main/install-bin.sh \| sh` | nothing |
| binary (manual) | download `scele-<os>-<arch>.tar.gz`, unpack, run `scele/scele` (link it onto `PATH`) | nothing |
| Python | `pipx install git+https://github.com/Andrew4Coding/scele-cli.git` | Python 3.10+, pipx |
| from clone | `./install.sh` / `.\install.ps1` | Python 3.10+ |
| npm (global) | `npm install -g scele-cli` (or `npx scele-cli`) | node >= 16 |
| agent skill | `npx skills add Andrew4Coding/scele-cli` | node |

The `install-bin.sh` / `install-bin.ps1` scripts always fetch the **latest** release unless
`SCELE_VERSION` is set, so they keep working across releases without edits.

## Checklist

- [ ] `pytest -q` green, `scele schema` runs
- [ ] `README.md` / `AGENTS.md` / `skills/scele/SKILL.md` reflect any command changes
- [ ] `scripts/release.sh <version>` → push tag
- [ ] Release workflow green; assets present on the Release page
- [ ] `curl … install-bin.sh | sh` on a clean machine installs and runs
