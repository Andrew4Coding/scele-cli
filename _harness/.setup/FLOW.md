# Setup Flow

## Goal

Turn a prompt-driven conversation into an initial working harness.
Focus on routing, policy, workflow, memory, GC, and guardrails before broad project narration.

## CRITICAL RULES

- **DO NOT skip user interaction**
- **DO NOT generate files before collecting user input**
- **MUST go through all stages and ask questions**
- Ask one small batch at a time
- Each stage requires user response before proceeding
- Summarize before generation and wait for confirmation
- Do not invent extra files or layers unless the user explicitly wants them

## Stage 1 — Understand the project and task types

Ask:

- What does this project do?
- What kind of tasks should agents help with?
- What language should documentation be in?

## Stage 2 — Understand workflow and confirmation boundaries

Ask:

- What are the main workflows?
- What should the agent do by default?
- What should always require confirmation?
- What usually does not require confirmation?

## Stage 3 — Understand structure, routing, and boundaries

Ask:

- What directories/modules matter most?
- How should README, harness docs, code, and memory stay separated?
- Are there protected areas the agent should avoid?
- Are there stack-specific commands or conventions?
- Any hard constraints or preferences?

## Stage 4 — Understand memory and GC

Ask:

- What should count as durable project memory?
- Should short-term memory be agent-specific?
- When should short-term memory be updated?
- Are there rules for pruning, compressing, or discarding noisy memory?

Default model:

- shared long-term memory: `_harness/memory/project.md`
- short-term local memory: `_harness/memory/agents/*.local.md`

## Stage 5 — Understand multi-agent needs

Ask:

- Is this a single-agent or multi-agent project?
- Should the harness integrate with existing local agents or roles?
- What lightweight roles should be recognized?

## Stage 6 — Generate files

Using templates in `_harness/.setup/templates/`, generate:

1. `_harness/readme.md` — project context and harness overview
2. `_harness/catalog.md` — project structure based on actual directories
3. `_harness/rules.md` — constraints and user preferences
4. `_harness/routing.md` — task-to-file mapping for common tasks
5. `_harness/workflow.md` — project-specific workflows
6. `_harness/memory/project.md` — initial project memory

Generation priorities:

- keep the harness minimal and composable
- prefer policy, routing, workflow, and guardrails over broad narration
- reflect real confirmation boundaries and memory rules
- do not create `_harness/agents.md`

## Stage 7 — Review and handoff

Summarize:

- what was generated
- what defaults were assumed
- which decisions should remain local vs become long-term memory
- how to evolve the harness later through review and explicit updates
