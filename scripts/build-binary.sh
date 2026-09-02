#!/usr/bin/env sh
# Build a standalone `scele` onedir bundle for the current OS/arch into ./dist/scele/.
#
#   scripts/build-binary.sh            -> dist/scele/scele  (dist/scele/scele.exe on Windows)
#
# onedir, not onefile: onefile re-extracts its archive on every run (seconds);
# onedir starts in ~0.1s. The release workflow ships dist/scele/ as a tarball.
#
# Requires: Python 3.10+ with the `build` extra ( pip install -e ".[build]" ).
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"

if [ -n "${PYTHON:-}" ]; then PYBIN="$PYTHON"
elif [ -x ".venv/bin/python" ]; then PYBIN=".venv/bin/python"
elif [ -x ".venv/Scripts/python.exe" ]; then PYBIN=".venv/Scripts/python.exe"
elif command -v python3 >/dev/null 2>&1; then PYBIN=python3
else PYBIN=python
fi

"$PYBIN" -c 'import PyInstaller' 2>/dev/null || {
    echo "PyInstaller missing. Run:  $PYBIN -m pip install -e \".[build]\"" >&2
    exit 1
}

"$PYBIN" -m PyInstaller packaging/scele.spec \
    --clean --noconfirm \
    --distpath dist --workpath build/pyinstaller

BIN="dist/scele/scele"
[ -f "$BIN.exe" ] && BIN="$BIN.exe"
echo
echo "Built: $BIN  (bundle: dist/scele/)"
"$BIN" --version
