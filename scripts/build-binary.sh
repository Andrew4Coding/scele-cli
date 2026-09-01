#!/usr/bin/env sh
# Build a standalone `scele` binary for the current OS/arch into ./dist/.
#
#   scripts/build-binary.sh            -> dist/scele            (or dist/scele.exe on Windows)
#   scripts/build-binary.sh --name X   -> dist/X
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

BIN="dist/scele"
[ -f "$BIN.exe" ] && BIN="$BIN.exe"
echo
echo "Built: $BIN"
"$BIN" --version
