#!/usr/bin/env sh
# Cross-platform installer for the `scele` CLI (Linux / macOS / WSL / Git-Bash).
#
#   ./install.sh                 install from this checkout, via pipx
#   ./install.sh --editable      install in editable mode (code changes apply live)
#   ./install.sh --from <src>    install from a path or git URL instead of this dir
#   ./install.sh --uninstall     remove it
#
# Needs: Python >= 3.10. Everything else (pip, pipx) is bootstrapped.
set -eu

EDITABLE=""
UNINSTALL=""
SRC=""
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

while [ $# -gt 0 ]; do
    case "$1" in
        -e|--editable) EDITABLE="1" ;;
        --uninstall)   UNINSTALL="1" ;;
        --from)        shift; SRC="${1:-}" ;;
        -h|--help)     sed -n '2,9p' "$0"; exit 0 ;;
        *) echo "unknown option: $1" >&2; exit 2 ;;
    esac
    shift
done
[ -n "$SRC" ] || SRC="$SCRIPT_DIR"

die() { echo "error: $*" >&2; exit 1; }

find_python() {
    for c in python3 python; do
        if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info[:2] >= (3,10) else 1)' 2>/dev/null; then
            command -v "$c"; return 0
        fi
    done
    return 1
}

PY=$(find_python) || die "Python >= 3.10 not found. Install it from https://www.python.org/downloads/ and re-run."
echo "Using $($PY --version) at $PY"

if ! command -v pipx >/dev/null 2>&1 && ! "$PY" -m pipx --version >/dev/null 2>&1; then
    echo "Installing pipx..."
    "$PY" -m pip install --user --upgrade pipx >/dev/null || die "could not install pipx"
fi
PIPX="pipx"
command -v pipx >/dev/null 2>&1 || PIPX="$PY -m pipx"

if [ -n "$UNINSTALL" ]; then
    $PIPX uninstall scele-cli || true
    echo "Removed. (Session cookie left in place; delete it manually if you want.)"
    exit 0
fi

$PIPX ensurepath >/dev/null 2>&1 || true

if [ -n "$EDITABLE" ]; then
    echo "Installing scele (editable) from $SRC ..."
    $PIPX install --force --editable "$SRC"
else
    echo "Installing scele from $SRC ..."
    $PIPX install --force "$SRC"
fi

echo
if command -v scele >/dev/null 2>&1; then
    echo "Installed: $(command -v scele)"
    echo "Next:  scele login   then   scele courses"
else
    echo "Installed, but 'scele' is not on your PATH yet."
    echo "Open a new terminal (or run:  $PIPX ensurepath  then restart your shell), then:"
    echo "    scele login"
fi
