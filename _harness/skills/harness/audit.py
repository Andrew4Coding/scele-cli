#!/usr/bin/env python3
import argparse
import math
import re
import sys
from pathlib import Path


CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from token_audit import DEFAULT_LOAD_MARKERS, iter_target_files, read_metrics, summarize


RELEVANT_FILES = [
    "AGENTS.md",
    "_harness/readme.md",
    "_harness/routing.md",
    "_harness/rules.md",
    "_harness/workflow.md",
    "_harness/catalog.md",
    "_harness/memory/project.md",
]


def read_text_if_exists(root: Path, relative_path: str):
    path = root / relative_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def verdict(score: float) -> str:
    if score >= 4.5:
        return "Strong"
    if score >= 3.5:
        return "Good"
    return "Weak"


def clamp(value: float, lower: float = 0.0, upper: float = 5.0) -> float:
    return max(lower, min(upper, value))


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


def score_harness(root: Path, files):
    totals = summarize(files)
    default_tokens = totals["default"]["tokens"]
    default_files = totals["default"]["files"]
    default_heaviest = max((item["tokens"] for item in files if item["scope"] == "default"), default=0)

    agents_text = read_text_if_exists(root, "AGENTS.md")
    routing_text = read_text_if_exists(root, "_harness/routing.md")
    rules_text = read_text_if_exists(root, "_harness/rules.md")
    workflow_text = read_text_if_exists(root, "_harness/workflow.md")
    memory_text = read_text_if_exists(root, "_harness/memory/project.md")
    readme_text = read_text_if_exists(root, "_harness/readme.md")

    entrypoint = 4.2
    if "Task classification" in agents_text:
        entrypoint += 0.5
    if "Then load only the minimum relevant documents from `_harness/`." in agents_text:
        entrypoint += 0.2
    if len(agents_text.splitlines()) <= 40:
        entrypoint += 0.1
    entrypoint = clamp(entrypoint)

    routing = 4.0
    if "Route by task before loading more files." in routing_text:
        routing += 0.3
    if "Boundary points" in routing_text:
        routing += 0.3
    if "capability or reusable skill questions" in routing_text:
        routing += 0.2
    if routing_text.count("->") >= 6:
        routing += 0.2
    routing = clamp(routing)

    boundaries = 4.0
    if "repo self-use" in readme_text and "template output" in readme_text and "runtime evaluation" in readme_text:
        boundaries += 0.4
    if "Do not use template files to express repo-internal policy." in rules_text:
        boundaries += 0.4
    if "README.md" in rules_text and "README.zh-CN.md" in rules_text:
        boundaries += 0.2
    boundaries = clamp(boundaries)

    workflow = 4.0
    if "Contract checks" in workflow_text and "Pass criteria" in workflow_text:
        workflow += 0.2
    if "Release" in workflow_text:
        workflow += 0.1
    if default_heaviest > 800:
        workflow -= 0.3
    if len(workflow_text.splitlines()) > 90:
        workflow -= 0.1
    workflow = clamp(workflow)

    memory = 3.8
    if memory_text:
        memory += 0.3
    if "durable decisions" in workflow_text:
        memory += 0.2
    if "_harness/memory/project.md" in agents_text and "_harness/memory/project.md" in routing_text:
        memory -= 0.1
    memory = clamp(memory)

    token_efficiency = 4.3
    if default_tokens > 3200:
        token_efficiency -= 0.6
    elif default_tokens > 2600:
        token_efficiency -= 0.2
    if default_files > 6:
        token_efficiency -= 0.2
    if default_heaviest > 800:
        token_efficiency -= 0.2
    token_efficiency = clamp(token_efficiency)

    dimensions = [
        ("Entrypoint clarity", entrypoint, "AGENTS.md is short and classifies tasks early."),
        ("Routing quality", routing, "routing.md is specific and layered by task type."),
        ("Rules and boundary clarity", boundaries, "repo, template, and sample boundaries are explicit."),
        ("Workflow usability", workflow, "workflow.md is actionable but is now the heaviest default-load file."),
        ("Memory and GC fit", memory, "project memory is useful, but memory ownership is split across files."),
        ("Token efficiency", token_efficiency, f"default-load cost is {default_tokens} estimated tokens."),
    ]
    overall = round(sum(score for _, score, _ in dimensions) / len(dimensions), 1)
    return dimensions, overall


def build_findings(root: Path, files):
    totals = summarize(files)
    default_files = [item for item in files if item["scope"] == "default"]
    top_default = max(default_files, key=lambda item: item["tokens"], default=None)
    findings = []

    if top_default and top_default["tokens"] >= 750:
        findings.append(
            (
                "Medium",
                "Workflow" if "workflow" in top_default["path"] else "Default-load",
                f"{top_default['path']} is the heaviest default-load file at about {top_default['tokens']} estimated tokens.",
                "Split or trim that file if more release or testing detail is added.",
            )
        )

    routing_text = read_text_if_exists(root, "_harness/routing.md")
    agents_text = read_text_if_exists(root, "AGENTS.md")
    if "minimum relevant" in routing_text and "minimum relevant" in agents_text:
        findings.append(
            (
                "Medium",
                "Routing",
                "The smallest-useful-context rule appears in both AGENTS.md and routing.md.",
                "Keep one canonical phrasing and let the other file refer to it.",
            )
        )

    if (root / "_harness/agents.md").exists():
        findings.append(
            (
                "Low",
                "Hidden policy",
                "_harness/agents.md exists but is not part of the main root routing path.",
                "Decide whether it is canonical or secondary and route to it explicitly if needed.",
            )
        )

    if totals["default"]["tokens"] > 2600:
        findings.append(
            (
                "Low",
                "Token efficiency",
                f"Default-load cost is {totals['default']['tokens']} estimated tokens across {totals['default']['files']} files.",
                "Keep default-load files short and push optional detail into secondary docs.",
            )
        )

    return findings


def build_recommendations(findings):
    fixes = []
    for _severity, _area, _finding, fix in findings:
        if fix not in fixes:
            fixes.append(fix)
    return fixes[:4]


def main():
    parser = argparse.ArgumentParser(
        description="Write a full harness audit report to markdown."
    )
    parser.add_argument("root", nargs="?", default=".", help="Project root to inspect")
    parser.add_argument("--output", default=".tmp/HARNESS_AUDIT.md", help="Markdown output path")
    parser.add_argument("--top", type=int, default=5, help="Top costly files to display")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files = [read_metrics(path, root) for path in iter_target_files(root)]
    totals = summarize(files)
    dimensions, overall = score_harness(root, files)
    findings = build_findings(root, files)
    recommendations = build_recommendations(findings)

    top_files = sorted(files, key=lambda item: item["tokens"], reverse=True)[: args.top]
    top_cost_rows = []
    for item in top_files:
        why = "biggest default-load pressure point" if item["scope"] == "default" else "high optional-load cost"
        top_cost_rows.append([item["path"], item["scope"], item["tokens"], why])

    primary_risk = findings[0][2] if findings else "No major risk detected"
    summary_rows = [
        ["Default-load tokens", totals["default"]["tokens"]],
        ["Optional-load tokens", totals["optional"]["tokens"]],
        ["Total tokens", totals["default"]["tokens"] + totals["optional"]["tokens"]],
        ["Default-load files", totals["default"]["files"]],
        ["Overall score", f"{overall} / 5"],
        ["Primary risk", primary_risk],
    ]
    score_rows = [
        [name, f"{score:.1f}", verdict(score), note]
        for name, score, note in dimensions
    ]
    score_rows.append(
        [
            "Overall",
            f"{overall:.1f}",
            verdict(overall),
            "Clear harness with moderate default-load bloat risk.",
        ]
    )
    finding_rows = [[severity, area, finding, fix] for severity, area, finding, fix in findings]
    if not finding_rows:
        finding_rows = [["Low", "Audit", "No material issues detected.", "Keep monitoring token growth."]]

    recommendation_lines = [f"{index}. {text}" for index, text in enumerate(recommendations, start=1)]
    if not recommendation_lines:
        recommendation_lines = ["1. Keep the current structure and watch token growth over time."]

    report = "\n".join(
        [
            "# HARNESS_AUDIT",
            "",
            "## Summary",
            "",
            render_table(["Metric", "Value"], summary_rows),
            "",
            "## Scorecard",
            "",
            render_table(["Dimension", "Score", "Verdict", "Notes"], score_rows),
            "",
            "## Top Cost Files",
            "",
            render_table(["File", "Scope", "Estimated tokens", "Why it matters"], top_cost_rows),
            "",
            "## Findings",
            "",
            render_table(["Severity", "Area", "Finding", "Recommended fix"], finding_rows),
            "",
            "## Recommended Fixes",
            "",
            *recommendation_lines,
            "",
        ]
    )

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = Path.cwd() / output_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
