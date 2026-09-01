#!/usr/bin/env python3
import argparse
import math
import re
from pathlib import Path


TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".toml"}
DEFAULT_LOAD_MARKERS = {
    "AGENTS.md",
    "_harness/readme.md",
    "_harness/routing.md",
    "_harness/catalog.md",
    "_harness/rules.md",
    "_harness/workflow.md",
}


def iter_target_files(root: Path):
    candidates = []
    agents = root / "AGENTS.md"
    if agents.exists():
        candidates.append(agents)

    harness = root / "_harness"
    if harness.exists():
        for path in sorted(harness.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() in TEXT_SUFFIXES:
                candidates.append(path)

    return candidates


def estimate_tokens(text: str) -> int:
    ascii_chars = sum(1 for char in text if ord(char) < 128)
    non_ascii_chars = len(text) - ascii_chars
    words = len(re.findall(r"\S+", text))
    heuristic = max((ascii_chars / 4.0) + (non_ascii_chars / 1.6), words * 1.3)
    return int(math.ceil(heuristic))


def classify_scope(rel_path: str) -> str:
    return "default" if rel_path in DEFAULT_LOAD_MARKERS else "optional"


def read_metrics(path: Path, root: Path):
    text = path.read_text(encoding="utf-8")
    rel_path = path.relative_to(root).as_posix()
    return {
        "path": rel_path,
        "scope": classify_scope(rel_path),
        "lines": len(text.splitlines()),
        "words": len(re.findall(r"\S+", text)),
        "bytes": len(text.encode("utf-8")),
        "tokens": estimate_tokens(text),
    }


def render_table(headers, rows):
    widths = []
    for index, header in enumerate(headers):
        values = [str(row[index]) for row in rows]
        widths.append(max(len(header), *(len(value) for value in values)))

    def render_row(values):
        cells = [str(value).ljust(widths[index]) for index, value in enumerate(values)]
        return "| " + " | ".join(cells) + " |"

    divider = "| " + " | ".join("-" * width for width in widths) + " |"
    return "\n".join([render_row(headers), divider, *(render_row(row) for row in rows)])


def summarize(files):
    totals = {
        "default": {"files": 0, "lines": 0, "words": 0, "tokens": 0},
        "optional": {"files": 0, "lines": 0, "words": 0, "tokens": 0},
    }
    for item in files:
        bucket = totals[item["scope"]]
        bucket["files"] += 1
        bucket["lines"] += item["lines"]
        bucket["words"] += item["words"]
        bucket["tokens"] += item["tokens"]
    return totals


def main():
    parser = argparse.ArgumentParser(
        description="Audit AGENTS.md and _harness token size with compact markdown tables."
    )
    parser.add_argument("root", nargs="?", default=".", help="Project root to inspect")
    parser.add_argument("--top", type=int, default=5, help="Top costly files to display")
    parser.add_argument("--output", help="Write the markdown report to this path")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files = [read_metrics(path, root) for path in iter_target_files(root)]
    totals = summarize(files)
    total_tokens = sum(item["tokens"] for item in files)

    summary_rows = [
        ["Default-load tokens", totals["default"]["tokens"]],
        ["Optional-load tokens", totals["optional"]["tokens"]],
        ["Total tokens", total_tokens],
        ["Default-load files", totals["default"]["files"]],
        ["Optional-load files", totals["optional"]["files"]],
        ["Measured files", len(files)],
    ]
    scope_rows = [
        ["Default-load set", totals["default"]["files"], totals["default"]["lines"], totals["default"]["words"], totals["default"]["tokens"]],
        ["Optional-load set", totals["optional"]["files"], totals["optional"]["lines"], totals["optional"]["words"], totals["optional"]["tokens"]],
    ]

    top_files = sorted(files, key=lambda item: item["tokens"], reverse=True)[: args.top]
    top_rows = [
        [item["path"], item["scope"], item["tokens"], item["lines"], item["words"]]
        for item in top_files
    ]

    report = "\n".join(
        [
            "# HARNESS_AUDIT",
            "",
            "## Summary",
            "",
            render_table(["Metric", "Value"], summary_rows),
            "",
            "## Scope Breakdown",
            "",
            render_table(["Scope", "Files", "Lines", "Words", "Estimated tokens"], scope_rows),
            "",
            "## Top Cost Files",
            "",
            render_table(["File", "Scope", "Estimated tokens", "Lines", "Words"], top_rows),
            "",
        ]
    )

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = Path.cwd() / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        print(f"Wrote {output_path}")
        return

    print(report)


if __name__ == "__main__":
    main()
