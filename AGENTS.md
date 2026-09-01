# AGENTS.md

This repository uses an AGENTS.md harness system.

## How to use this file

**If you just ran `npx agents-md-harness setup`** (or the legacy `init` alias):

You now have the harness framework, but the core files don't exist yet. Tell your AI agent:

> "Help me setup the harness"

The agent will guide you through a conversation to generate customized harness files based on your project.

**If harness files already exist:**

Continue to "Normal usage" section below.

## First-time setup

If `_harness/` core files (readme.md, routing.md, catalog.md, rules.md, workflow.md) don't exist yet:

**You MUST enter setup conversation mode. DO NOT generate files directly.**

### Setup conversation steps:

1. Read `_harness/.setup/PROMPT.md` and `_harness/.setup/FLOW.md`
2. Tell the user: "I need to set up the harness through a conversation. Let me ask you some questions."
3. Go through each stage in FLOW.md, asking questions and waiting for responses:
   - Stage 1: Project and task types
   - Stage 2: Workflow and confirmation boundaries
   - Stage 3: Structure, routing, and boundaries
   - Stage 4: Memory and GC model
   - Stage 5: Multi-agent needs
4. After collecting all answers, summarize and ask: "Should I generate the harness files with this configuration?"
5. Only after user confirms, generate files using templates in `_harness/.setup/templates/`

**Files to generate:**

- `_harness/readme.md`
- `_harness/routing.md`
- `_harness/catalog.md`
- `_harness/rules.md`
- `_harness/workflow.md`
- `_harness/memory/project.md`

## Normal usage

Once harness is set up:

1. Read this file first
2. Classify the task
3. Load only the minimum relevant documents from `_harness/`

### Routing

- Project overview → `_harness/readme.md`
- Task-to-file routing → `_harness/routing.md`
- Project structure lookup → `_harness/catalog.md`
- Hard rules and constraints → `_harness/rules.md`
- Execution procedures → `_harness/workflow.md`

### Loading Principles

- Prefer minimum necessary reads
- Route before loading
- Load the most relevant file first
- Combine multiple files only when truly needed

## Memory

- Shared long-term memory: `_harness/memory/project.md`
- Per-agent short-term memory: `_harness/memory/agents/*.local.md`

## Evolution

This harness evolves with the project:

- Core harness files can be updated through user-approved proposals
- When harness is insufficient, propose changes and wait for approval
- See `_harness/rules.md` for evolution rules and risk levels
