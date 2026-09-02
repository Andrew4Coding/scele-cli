#!/usr/bin/env sh
# Download a prebuilt `scele` from GitHub Releases. No Python needed.
#
#   curl -fsSL https://raw.githubusercontent.com/Andrew4Coding/scele-cli/main/install-bin.sh | sh
#
# Env overrides:
#   SCELE_VERSION=v0.2.0            install a specific tag (default: latest)
#   SCELE_BIN_DIR=/usr/local/bin    where the `scele` launcher goes (default: ~/.local/bin)
#   SCELE_APP_DIR=~/.local/lib/scele-app   where the bundle is unpacked
set -eu

REPO="Andrew4Coding/scele-cli"
VERSION="${SCELE_VERSION:-latest}"
BIN_DIR="${SCELE_BIN_DIR:-$HOME/.local/bin}"
APP_DIR="${SCELE_APP_DIR:-$HOME/.local/lib/scele-app}"

die() { echo "error: $*" >&2; exit 1; }

os=$(uname -s)
arch=$(uname -m)
case "$os" in
    Linux)  OS=linux ;;
    Darwin) OS=macos ;;
    *) die "unsupported OS '$os'. Use: pipx install git+https://github.com/$REPO.git" ;;
esac
case "$arch" in
    x86_64|amd64)  ARCH=x86_64 ;;
    arm64|aarch64) [ "$OS" = macos ] && ARCH=arm64 || ARCH=aarch64 ;;
    *) die "unsupported architecture '$arch'" ;;
esac
ASSET="scele-${OS}-${ARCH}.tar.gz"

if [ "$VERSION" = latest ]; then
    BASE="https://github.com/$REPO/releases/latest/download"
else
    BASE="https://github.com/$REPO/releases/download/$VERSION"
fi

fetch() {
    if command -v curl >/dev/null 2>&1; then curl -fsSL "$1" -o "$2"
    elif command -v wget >/dev/null 2>&1; then wget -qO "$2" "$1"
    else die "need curl or wget"; fi
}
sha256() {
    if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | awk '{print $1}'
    elif command -v shasum >/dev/null 2>&1; then shasum -a 256 "$1" | awk '{print $1}'
    else echo ""; fi
}

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

echo "Downloading $ASSET ($VERSION)..."
fetch "$BASE/$ASSET" "$tmp/$ASSET" \
    || die "download failed — no prebuilt bundle for $OS-$ARCH at $BASE. Try: pipx install git+https://github.com/$REPO.git"

if fetch "$BASE/checksums.txt" "$tmp/checksums.txt" 2>/dev/null && [ -s "$tmp/checksums.txt" ]; then
    want=$(grep " ${ASSET}\$" "$tmp/checksums.txt" | awk '{print $1}' || true)
    got=$(sha256 "$tmp/$ASSET")
    if [ -n "$want" ] && [ -n "$got" ] && [ "$want" != "$got" ]; then
        die "checksum mismatch for $ASSET"
    fi
    [ -n "$want" ] && echo "checksum ok"
fi

# Unpack the onedir bundle. The tarball's top-level dir is `scele/`; land its
# contents directly in $APP_DIR so the launcher is $APP_DIR/scele.
rm -rf "$APP_DIR"
mkdir -p "$APP_DIR"
tar -xzf "$tmp/$ASSET" -C "$APP_DIR" --strip-components=1
[ -x "$APP_DIR/scele" ] || die "bundle missing its launcher (extracted to $APP_DIR)"
[ "$OS" = macos ] && xattr -dr com.apple.quarantine "$APP_DIR" 2>/dev/null || true

mkdir -p "$BIN_DIR"
ln -sf "$APP_DIR/scele" "$BIN_DIR/scele"
echo "Installed: $BIN_DIR/scele -> $APP_DIR/scele"
"$BIN_DIR/scele" --version >/dev/null 2>&1 || true

case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *) echo
       echo "Add $BIN_DIR to your PATH:"
       echo "    echo 'export PATH=\"$BIN_DIR:\$PATH\"' >> ~/.$(basename "${SHELL:-bash}")rc" ;;
esac
echo
echo "Next:  scele login   then   scele courses"
