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

# --- UI & Styling Setup ---
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ] && [ "${TERM:-}" != "dumb" ]; then
    BOLD="\033[1m"
    DIM="\033[2m"
    RESET="\033[0m"
    RED="\033[31m"
    GREEN="\033[32m"
    YELLOW="\033[33m"
    BLUE="\033[34m"
    CYAN="\033[36m"
    GOLD="\033[1;33m"
    CLEAR_LINE="\033[2K\r"
    HIDE_CURSOR="\033[?25l"
    SHOW_CURSOR="\033[?25h"
    TICK="✔"
    CROSS="✖"
    INFO="ℹ"
else
    BOLD=""
    DIM=""
    RESET=""
    RED=""
    GREEN=""
    YELLOW=""
    BLUE=""
    CYAN=""
    GOLD=""
    CLEAR_LINE=""
    HIDE_CURSOR=""
    SHOW_CURSOR=""
    TICK="[OK]"
    CROSS="[FAIL]"
    INFO="[!]"
fi

# Cleanup and cursor restoration on exit/interrupt
TMP_DIR=""
CURRENT_PID=""
cleanup() {
    exit_code=$?
    [ -n "$CURRENT_PID" ] && kill -9 "$CURRENT_PID" 2>/dev/null || true
    [ -t 1 ] && printf "%b" "$SHOW_CURSOR"
    [ -n "$TMP_DIR" ] && rm -rf "$TMP_DIR"
    exit "$exit_code"
}
trap cleanup EXIT INT TERM

die() {
    printf "\n  ${RED}%s${RESET} ${BOLD}Error:${RESET} %s\n\n" "$CROSS" "$*" >&2
    exit 1
}

print_banner() {
    printf "\n"
    printf "${GOLD}     _____ _____ _____ __    _____ ${RESET}\n"
    printf "${GOLD}    |   __|     |   __|  |  |   __|${RESET}\n"
    printf "${GOLD}    |__   |   --|   __|  |__|   __|${RESET}\n"
    printf "${GOLD}    |_____|_____|_____|_____|_____|${RESET}  ${CYAN}CLI${RESET}\n"
    printf "    ${DIM}Moodle client for CS Universitas Indonesia (scele.cs.ui.ac.id)${RESET}\n"
    printf "\n"
}

run_step() {
    step_num="$1"
    total_steps="$2"
    step_desc="$3"
    shift 3

    step_log="$TMP_DIR/step-$step_num.log"

    if [ -t 1 ] && [ -z "${NO_COLOR:-}" ] && [ "${TERM:-}" != "dumb" ]; then
        "$@" >"$step_log" 2>&1 &
        CURRENT_PID=$!
        i=0
        printf "%b" "$HIDE_CURSOR"
        while kill -0 "$CURRENT_PID" 2>/dev/null; do
            case $i in
                0) frame="⠋" ;; 1) frame="⠙" ;; 2) frame="⠹" ;; 3) frame="⠸" ;; 4) frame="⠼" ;;
                5) frame="⠴" ;; 6) frame="⠦" ;; 7) frame="⠧" ;; 8) frame="⠇" ;; 9) frame="⠏" ;;
            esac
            i=$(( (i + 1) % 10 ))
            printf "\r  ${CYAN}%s${RESET} ${BOLD}[%s/%s]${RESET} %s..." "$frame" "$step_num" "$total_steps" "$step_desc"
            sleep 0.08
        done
        wait "$CURRENT_PID"
        status=$?
        CURRENT_PID=""
        printf "%b" "$SHOW_CURSOR"

        if [ "$status" -eq 0 ]; then
            printf "\r${CLEAR_LINE}  ${GREEN}%s${RESET} ${BOLD}[%s/%s]${RESET} %s\n" "$TICK" "$step_num" "$total_steps" "$step_desc"
            return 0
        else
            printf "\r${CLEAR_LINE}  ${RED}%s${RESET} ${BOLD}[%s/%s]${RESET} %s ${RED}(failed)${RESET}\n" "$CROSS" "$step_num" "$total_steps" "$step_desc"
            if [ -s "$step_log" ]; then
                printf "\n${RED}%s${RESET}\n" "$(cat "$step_log")" >&2
            fi
            return "$status"
        fi
    else
        printf "  [%s/%s] %s...\n" "$step_num" "$total_steps" "$step_desc"
        "$@" >"$step_log" 2>&1
        status=$?
        if [ "$status" -eq 0 ]; then
            printf "  [%s/%s] %s (done)\n" "$step_num" "$total_steps" "$step_desc"
            return 0
        else
            printf "  [%s/%s] %s (failed)\n" "$step_num" "$total_steps" "$step_desc"
            if [ -s "$step_log" ]; then
                cat "$step_log" >&2
            fi
            return "$status"
        fi
    fi
}

show_help() {
    print_banner
    printf "Cross-platform installer for the 'scele' CLI (Linux / macOS / WSL / Git-Bash).\n\n"
    printf "Usage:\n"
    printf "  ./install.sh                 Install from this checkout via pipx\n"
    printf "  ./install.sh --editable      Install in editable mode (code changes apply live)\n"
    printf "  ./install.sh --from <src>    Install from a path or git URL instead of this dir\n"
    printf "  ./install.sh --uninstall     Remove scele-cli\n"
    printf "  ./install.sh --help          Show this help message\n\n"
    printf "Requirements:\n"
    printf "  Python >= 3.10 (pip and pipx will be bootstrapped automatically).\n\n"
    exit 0
}

while [ $# -gt 0 ]; do
    case "$1" in
        -e|--editable) EDITABLE="1" ;;
        --uninstall)   UNINSTALL="1" ;;
        --from)        shift; SRC="${1:-}" ;;
        -h|--help)     show_help ;;
        *) echo "unknown option: $1" >&2; exit 2 ;;
    esac
    shift
done
[ -n "$SRC" ] || SRC="$SCRIPT_DIR"

find_python() {
    for c in python3 python; do
        if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info[:2] >= (3,10) else 1)' 2>/dev/null; then
            command -v "$c"; return 0
        fi
    done
    return 1
}

TMP_DIR=$(mktemp -d)

print_banner

# Step 1: Detect Python
PY=$(find_python) || die "Python >= 3.10 not found. Install it from https://www.python.org/downloads/ and re-run."
PY_VER=$("$PY" --version 2>&1)

if [ -n "$UNINSTALL" ]; then
    PIPX="pipx"
    command -v pipx >/dev/null 2>&1 || PIPX="$PY -m pipx"

    uninstall_scele() {
        $PIPX uninstall scele-cli || true
    }
    run_step 1 1 "Uninstalling scele-cli via pipx" uninstall_scele

    printf "\n  ${GREEN}%s${RESET} ${BOLD}Successfully removed scele-cli.${RESET}\n" "$TICK"
    printf "  ${DIM}(Auth token left in ~/.config/scele/token.json; run 'scele logout' if desired.)${RESET}\n\n"
    exit 0
fi

TOTAL_STEPS=4

printf "  ${GREEN}%s${RESET} ${BOLD}[1/%s]${RESET} Detected Python: ${CYAN}%s${RESET} ${DIM}(%s)${RESET}\n" "$TICK" "$TOTAL_STEPS" "$PY_VER" "$PY"

# Step 2: Bootstrap or check pipx
install_pipx() {
    "$PY" -m pip install --user --upgrade pipx
}

if ! command -v pipx >/dev/null 2>&1 && ! "$PY" -m pipx --version >/dev/null 2>&1; then
    run_step 2 "$TOTAL_STEPS" "Bootstrapping pipx package runner" install_pipx \
        || die "could not install pipx"
else
    PIPX_VER=$(pipx --version 2>/dev/null || "$PY" -m pipx --version 2>/dev/null || echo "ready")
    printf "  ${GREEN}%s${RESET} ${BOLD}[2/%s]${RESET} pipx is available: ${CYAN}v%s${RESET}\n" "$TICK" "$TOTAL_STEPS" "$PIPX_VER"
fi

PIPX="pipx"
command -v pipx >/dev/null 2>&1 || PIPX="$PY -m pipx"

# Step 3: Configure PATH
ensure_paths() {
    $PIPX ensurepath >/dev/null 2>&1 || true
}
run_step 3 "$TOTAL_STEPS" "Configuring environment PATH via pipx" ensure_paths

# Step 4: Install package
install_pkg() {
    if [ -n "$EDITABLE" ]; then
        $PIPX install --force --editable "$SRC"
    else
        $PIPX install --force "$SRC"
    fi
}

INSTALL_DESC="Installing scele from $SRC"
[ -n "$EDITABLE" ] && INSTALL_DESC="Installing scele (editable) from $SRC"
run_step 4 "$TOTAL_STEPS" "$INSTALL_DESC" install_pkg \
    || die "failed to install scele via pipx"

# Summary & Next Steps
printf "\n"
if command -v scele >/dev/null 2>&1; then
    BIN_LOC=$(command -v scele)
    INSTALLED_VER=$("$BIN_LOC" --version 2>/dev/null || echo "scele")

    printf "  ${GREEN}%s${RESET} ${BOLD}SCELE CLI installed successfully!${RESET}\n\n" "$TICK"
    printf "  ${CYAN}│${RESET}  ${BOLD}Location:${RESET}  %s\n" "$BIN_LOC"
    printf "  ${CYAN}│${RESET}  ${BOLD}Source:${RESET}    %s\n" "$SRC"
    printf "  ${CYAN}│${RESET}  ${BOLD}Version:${RESET}   %s\n\n" "$INSTALLED_VER"
    printf "  ${BOLD}Quick Start:${RESET}\n"
    printf "    ${CYAN}scele login${RESET}     Authenticate with your SCELE account\n"
    printf "    ${CYAN}scele courses${RESET}   List your enrolled courses\n"
    printf "    ${CYAN}scele --help${RESET}    Explore available commands and options\n\n"
else
    printf "  ${YELLOW}%s Notice:${RESET} 'scele' was installed, but is not on your PATH yet.\n" "$INFO"
    printf "  Open a new terminal tab (or run: ${CYAN}%s ensurepath${RESET} then restart shell), then run:\n\n" "$PIPX"
    printf "    ${CYAN}scele login${RESET}\n\n"
fi
