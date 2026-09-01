---
name: harness
purpose: Inspect and improve AGENTS.md and _harness quality as a reusable harness capability
triggers:
  - Audit the current harness
  - Estimate AGENTS.md and _harness token cost
  - Review harness prompt quality, routing quality, or instruction quality
inputs:
  - Root AGENTS.md
  - Relevant files under _harness/
  - Optional command such as audit, audit tokens, or audit quality
outputs:
  - `.tmp/HARNESS_AUDIT.md`
  - Markdown tables for token and score summaries
  - Audit findings by severity
  - Quality score with reasoning
  - Recommended fixes
---

# Harness

## Goal

Provide a single harness-focused capability that inspects `AGENTS.md` and `_harness/`.
This skill is for harness self-audit, not product-code review.

## Support tool

Use `audit.py` for the full report:

```bash
python3 _harness/skills/harness/audit.py . --output .tmp/HARNESS_AUDIT.md
```

The full audit writes a compact report with:

- summary
- scorecard
- top cost files
- findings
- recommended fixes

Use `token_audit.py` when you only want the token tables:

```bash
python3 _harness/skills/harness/token_audit.py . --output .tmp/HARNESS_AUDIT.md
```

The token-only script reports compact Markdown tables for:

- summary metrics
- scope breakdown
- top cost files

The default audit artifact path is `.tmp/HARNESS_AUDIT.md`.

## Commands

### `audit`

Run the full harness review.

Procedure:

1. Read `AGENTS.md` first.
2. Load only the minimum `_harness/` files needed for the requested review.
3. Ensure `.tmp/` exists.
4. Run `python3 _harness/skills/harness/audit.py . --output .tmp/HARNESS_AUDIT.md`.
5. Let the script write the full report.
6. In the terminal, print only a short completion note with the output path.

Return these sections in order:

1. Summary
2. Scorecard
3. Top cost files
4. Findings
5. Recommended fixes

### `audit tokens`

Focus on token count, context size, and likely read cost.

Procedure:

1. Run `python3 _harness/skills/harness/token_audit.py .`.
2. Prefer `python3 _harness/skills/harness/token_audit.py . --output .tmp/HARNESS_AUDIT.md`.
3. Write the token report into `.tmp/HARNESS_AUDIT.md`.
4. Highlight default-load cost vs optional-load cost.
5. Call out the highest-cost files and whether each one is justified.

### `audit quality`

Focus on instruction quality and harness usability.

Procedure:

1. Read `AGENTS.md`.
2. Read only the `_harness/` files needed to judge routing, boundaries, workflow, memory, and drift risk.
3. Prefer `python3 _harness/skills/harness/audit.py . --output .tmp/HARNESS_AUDIT.md`.
4. Let the script write the scorecard and findings tables.
5. In the terminal, print only the output path.

## When to use

Use this skill when the user asks to:

1. Check harness quality.
2. Score the current harness.
3. Estimate token size or context cost.
4. Review prompt quality, routing quality, or instruction quality.
5. Compare harness revisions before release.

## Audit dimensions

Score each dimension from 0-5:

- Entrypoint clarity
- Routing quality
- Rules and boundary clarity
- Workflow usability
- Memory and GC fit
- Token efficiency

Then provide one overall score from 0-5 with one sentence of justification.

## Report format

Use short sections and Markdown tables.
Do not output one long prose block.
Do not dump every measured file unless the user explicitly asks for full detail.
Write the full report to `.tmp/HARNESS_AUDIT.md`.
Prefer a short terminal note like `Wrote .tmp/HARNESS_AUDIT.md`.

### Summary table

| Metric               |   Value |
| -------------------- | ------: |
| Default-load tokens  |     ... |
| Optional-load tokens |     ... |
| Total tokens         |     ... |
| Default-load files   |     ... |
| Overall score        | ... / 5 |
| Primary risk         |     ... |

### Scorecard table

| Dimension                  | Score | Verdict              | Notes                 |
| -------------------------- | ----: | -------------------- | --------------------- |
| Entrypoint clarity         |   0-5 | Strong / Good / Weak | Short rationale       |
| Routing quality            |   0-5 | Strong / Good / Weak | Short rationale       |
| Rules and boundary clarity |   0-5 | Strong / Good / Weak | Short rationale       |
| Workflow usability         |   0-5 | Strong / Good / Weak | Short rationale       |
| Memory and GC fit          |   0-5 | Strong / Good / Weak | Short rationale       |
| Token efficiency           |   0-5 | Strong / Good / Weak | Short rationale       |
| Overall                    |   0-5 | Strong / Good / Weak | One-sentence judgment |

### Top cost files table

| File | Scope              | Estimated tokens | Why it matters |
| ---- | ------------------ | ---------------: | -------------- |
| ...  | default / optional |              ... | ...            |

### Findings table

| Severity            | Area                                     | Finding | Recommended fix |
| ------------------- | ---------------------------------------- | ------- | --------------- |
| High / Medium / Low | Routing / Workflow / Memory / Boundaries | ...     | ...             |

## Constraints

- Audit the harness itself unless the user explicitly asks for product code too.
- Treat token counts as estimates unless measured with a model-specific tokenizer.
- Prefer concrete findings over vague style commentary.
- Call out conflicts between README, `AGENTS.md`, and `_harness/` when they affect agent behavior.
- Keep the output operational: tables, findings, score, and fix list.
