---
name: develop-synthesis
description: Strategic synthesis step for /develop — transforms a seed + research handoff into a TL;DR card. Invoked by the /develop orchestrator after research is complete, or directly for testing. Takes an idea name; reads the seed file and research handoff, applies strategic reasoning to produce the card.
argument-hint: [idea-name]
context: fork
agent: develop-synthesis
disable-model-invocation: false
allowed-tools:
  - Read
  - Edit
  - Glob
  - Grep
  - Bash(date:*)
---

# /develop-synthesis — Strategic Synthesis Step

Transforms a seed-stage idea and its research handoff into a completed TL;DR card. This is the judgment-heavy step of the /develop pipeline — the agent carries the strategic reasoning framework.

Normally invoked by the /develop orchestrator after research (Steps 0-4) is complete. Can also be invoked directly for testing or re-synthesis.

## Arguments

Parse `$ARGUMENTS` to resolve the target idea file.

| Input | Behavior |
| ------- | ---------- |
| Empty | Report error: idea name required. Exit. |
| `idea-name` | Resolve to `Ideas/{idea-name}.md` |
| `idea-name.md` | Strip `.md`, resolve as above |

If exact match fails, try fuzzy substring match against filenames in `Ideas/`. One match: use it. Multiple: list and exit. Zero: report and exit.

## Execution

### Step 0: Parse Arguments

1. Read `$ARGUMENTS`
2. If empty: report "Error: idea name required." and exit.
3. If provided: resolve to `Ideas/{argument}.md`
   - Try exact match first (with and without `.md` extension)
   - If not found, try fuzzy substring match against all filenames in `Ideas/`
   - If exactly one fuzzy match, use it
   - If multiple fuzzy matches, list and exit
   - If zero matches, report available files and exit

### Step 1: Load Context

Load in parallel:

1. **Seed file** — `Ideas/{idea-name}.md` (full content)
2. **Research handoff** — `Research/{idea-name}/synthesis-handoff.md`
   - If not found: report "No research handoff found at Research/{idea-name}/synthesis-handoff.md — run /develop research phase first or create manually for testing." Exit.
3. **Persona guide** — `persona.md`
4. **Format example** — `Examples/developing-card.md`
5. **Related ideas** — Read the `related-ideas` array from the seed's frontmatter. For each entry, read `Ideas/{related-idea}.md` up to the first `###` heading or 30 lines — enough to get frontmatter and header fields (Core insight, Problem, Who cares, Strategic connection). If the handoff includes a Portfolio Context section, use that instead of reading files.

### Step 2: Validate

Confirm:

- Seed file exists and has `stage: seed` in frontmatter
- Research handoff exists and is non-empty
- Persona guide loads successfully

If seed is not at `stage: seed`: report current stage and exit. The orchestrator is responsible for validating stage before invocation; this is a safety check.

### Step 3: Synthesize

Apply the reasoning dimensions from the agent definition (The User's Moment, The Single Strategic Move, The Compound, The Strategic Connection, The Unique Territory) to produce the TL;DR card content. The agent definition carries the full reasoning framework, rubrics, voice requirements, and output template.

Write the completed card to the idea file:

- Update frontmatter (stage, updated date, impact dimensions)
- Replace body content above `### Original Capture` with the TL;DR template
- Preserve `### Original Capture`

### Step 4: Report

Present what was produced:

```text
Synthesis complete: {idea-name}

Impact dimensions: {CS}/{UX}/{RP}/{ID}/{SA}
Card written to: Ideas/{idea-name}.md
```

## Error Handling

| Condition | Behavior |
| ----------- | ---------- |
| No argument provided | Report: idea name required. Exit. |
| Idea file not found | Fuzzy match, report available files. Exit. |
| Research handoff not found | Report: run research phase first. Exit. |
| Seed not at seed stage | Report current stage. Exit. |
| Persona guide not found | Report: missing persona guide. Exit. |
