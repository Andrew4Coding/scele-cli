#!/usr/bin/env sh
# Cut a release: bump the version, commit, tag, push. CI builds the binaries.
#
#   scripts/release.sh 0.2.0
#
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"

VERSION="${1:-}"
[ -n "$VERSION" ] || { echo "usage: scripts/release.sh <version>  (e.g. 0.2.0)" >&2; exit 2; }
echo "$VERSION" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+([.-][0-9A-Za-z.]+)?$' \
    || { echo "error: '$VERSION' is not a valid version" >&2; exit 1; }

[ -z "$(git status --porcelain)" ] || { echo "error: working tree is dirty" >&2; exit 1; }
[ "$(git rev-parse --abbrev-ref HEAD)" = main ] || echo "warning: not on main"

INIT="src/scele/__init__.py"
python3 - "$INIT" "$VERSION" <<'PY'
import re, sys
path, version = sys.argv[1], sys.argv[2]
text = open(path).read()
text = re.sub(r'__version__ = "[^"]*"', f'__version__ = "{version}"', text, count=1)
open(path, "w").write(text)
PY

git add "$INIT"

if [ -f "package.json" ]; then
    python3 - "$VERSION" <<'PY'
import json, sys
version = sys.argv[1]
with open("package.json", "r") as f:
    pkg = json.load(f)
pkg["version"] = version
with open("package.json", "w") as f:
    json.dump(pkg, f, indent=2)
    f.write("\n")
PY
    git add package.json
fi

git commit -m "release: v$VERSION"
git tag -a "v$VERSION" -m "v$VERSION"

echo
echo "Committed and tagged v$VERSION. Push to trigger the Release workflow:"
echo "    git push origin main --follow-tags"
