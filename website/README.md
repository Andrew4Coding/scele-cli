# scele-cli docs website

Landing page + documentation for `scele`, built with [Zensical](https://zensical.org/).

## Develop

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install zensical
zensical serve          # http://localhost:8000, live reload
zensical build          # -> ./site (git-ignored)
```

## Structure

```
zensical.toml                 site + theme config: navbar, nav tree, SCELE-gold palette
docs/
  index.md                    landing page: hero, features, install tabs, footer
  commands/
    index.md                  all 31 commands in one table
    account/ courses/ planning/ catalog/
    forums/ assignments/ files/ announcements/ tools/
                              one page per command
  report.md                   issue form -> prefilled GitHub issue
  credits.md                  contributors, pulled live from the GitHub API
  stylesheets/extra.css       palette + hero, feature grid, issue form, contributors
  javascripts/extra.js        platform-aware install command, issue-URL builder,
                              contributor fetch, image placeholders
  assets/features/*.png       landing-page feature images   (add your own)
  assets/commands/*.png       per-command output screenshots (add your own)
```

The site is deliberately narrow: a landing page, the command reference, an issue form and
credits. There is no Getting-started section and no quiz documentation.

## Images to add

Both directories are empty on purpose — until a file exists, the page shows a dashed
placeholder box instead.

**`docs/assets/features/`** — one per landing-page card:
`login.png`, `courses.png`, `deadlines.png`, `forum.png`, `assignments.png`,
`resources.png`, `watch.png`

**`docs/assets/commands/`** — a screenshot of each command's real output, named after the
command: `courses.png`, `deadlines.png`, `submit.png`, … one per page under
`docs/commands/`. Every command page already references `../../assets/commands/<name>.png`.

## Theme

The palette is SCELE gold (`#f2b705`), defined once at the top of
`docs/stylesheets/extra.css`. In light mode the header carries the gold with dark text; in
dark mode the header goes near-black and the gold moves to links, accents, and the active
nav item — the only way yellow stays readable in both schemes.

`variant = "classic"` in `zensical.toml` is what lets the header take the brand colour; the
`modern` variant keeps its chrome deliberately neutral. The `toc.integrate` feature folds
each page's table of contents into the **left** sidebar instead of a separate right column.
The header brand mark is hidden in CSS — the `scele-cli` wordmark carries it.

## Command pages

The pages under `docs/commands/` were generated from `scele schema` — the CLI's own
manifest — and then hand-written prose, notes, and cross-links were added. They are plain
Markdown: edit them directly.

When a command is added, renamed, or its options change, update the matching page here
alongside `README.md` and `skills/scele/SKILL.md` in the repository root, and add it to the
`nav` in `zensical.toml`.

## Deploy (GitHub Pages)

Move `.github/workflows/docs.yml` to the repository root at `.github/workflows/docs.yml`,
push, then set **Settings → Pages → Source: GitHub Actions**.
