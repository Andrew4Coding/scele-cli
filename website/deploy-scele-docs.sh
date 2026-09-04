#!/usr/bin/env bash
# Rebuild the scele-cli docs site from git and publish it.
# nginx serves $REPO/website/site directly, so no reload is needed.
#   usage: ~/deploy-scele-docs.sh [branch]     (default: docs)
set -euo pipefail

REPO=/home/andrew/scele-cli
BRANCH="${1:-docs}"
SITE_URL="https://scele.andrewaryo.com/"

cd "$REPO"
git fetch --prune origin "$BRANCH"
git checkout -q "$BRANCH"
git reset --hard -q "origin/$BRANCH"
echo "at $(git log --oneline -1)"

cd "$REPO/website"

# The docs branch still targets GitHub Pages. Retarget for this host, and put
# the file back afterwards so the tree stays clean.
# Once site_url is committed upstream as $SITE_URL, this becomes a no-op.
sed -i "s|^site_url = .*|site_url = \"$SITE_URL\"|" zensical.toml

[ -x .venv/bin/zensical ] || { python3 -m venv .venv; .venv/bin/pip install -q zensical; }
.venv/bin/zensical build

git checkout -- zensical.toml

# nginx (www-data) needs to traverse in and read the output
chmod -R a+rX "$REPO/website/site"
echo "published $(find site -type f | wc -l) files -> $REPO/website/site"
