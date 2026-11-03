---
name: buildable-surface
description: This skill should be used when the user asks to "check buildable surface for [idea]", "generate feature candidates for [idea]", "buildable surface [idea]", "what could we build for [idea]", or "surface candidates for [idea]". Detects principle-shaped Thought Outlines and generates distinct product approach candidates. No-ops on feature-shaped ideas.
argument-hint: [idea-name]
context: fork
agent: buildable-surface
disable-model-invocation: false
allowed-tools:
  - Read
  - Edit
  - Glob
  - Grep
  - Bash(date:*)
  - mcp__obsidian__read_note
  - mcp__obsidian__patch_note
  - mcp__obsidian__update_frontmatter
---

# /buildable-surface — Buildable Surface Enrichment Agent

Detects whether a developed idea's Thought Outline describes a strategic principle (principle-shaped) or a specific buildable capability (feature-shaped). For principle-shaped ideas, generates 3-5 distinct product approach candidates. For feature-shaped ideas, no-ops.

This is an enrichment agent, not a stage transition workflow. It does not change the idea's stage.

## Invocation

```text
/buildable-surface [idea-name]
```

- Required argument: the name of a developing-or-later idea file in `Ideas/`
- Works on ideas at developing, drafting, refining, or complete stages (must have a Thought Outline)
- Examples: `/buildable-surface foraging-intelligence`, `/buildable-surface cache-optimization`

**Idea-only by design.** This skill has no `--adhoc` mode. Its value proposition is classifying an idea's Thought Outline as principle-shaped vs. feature-shaped — an idea-shape question that has no analogue when run against a free-form subject. The other five enrichment skills (edtech-sme, educator-sme, divergent-thinking, tam-estimate, cross-domain) support `--adhoc`; buildable-surface intentionally does not.

## Arguments

Parse `$ARGUMENTS` to resolve the target idea file.

**Resolution rules:**

| Input | Behavior |
| ------- | ---------- |
| Empty | List all developing-or-later ideas in Ideas/, ask user to select |
| `idea-name` | Resolve to `Ideas/{idea-name}.md` |
| `idea-name.md` | Strip `.md`, resolve as above |

**Fuzzy matching:** If exact match fails, list all `.md` files in Ideas/ and find filenames containing the argument as a substring (case-insensitive). If exactly one match, use it. If multiple matches, present options and ask user to pick. If zero matches, report and exit.

## Persona

This skill runs in the buildable-surface agent's context. The agent carries the product strategist persona, detection heuristic, candidate quality standards, and appetite bounding framework. See `.claude/agents/buildable-surface.md`.

## Execution Flow

Execute these steps in order. Stop and report errors at any step rather than continuing with bad data.

### Step 0: Parse Arguments

1. Read `$ARGUMENTS`
2. If empty: use `Glob` to list all `.md` files in `Ideas/`. Read the first 20 lines of each to check frontmatter for `stage:` value. Present ideas at developing or later stages (developing, drafting, refining, complete) to the user and ask them to select one. If none exist, report "No developing-or-later ideas found in Ideas/" and exit.
3. If provided: attempt to resolve `Ideas/{argument}.md`
   - Try exact match first (with and without `.md` extension)
   - If not found, try fuzzy substring match against all filenames in Ideas/
   - If exactly one fuzzy match, use it
   - If multiple fuzzy matches, present options and ask user to pick
   - If zero matches, report "Idea file not found: {argument}. Available files in Ideas/: {list}" and exit

### Step 1: Load Context

Load in parallel:

1. **Idea file** at the resolved path — full content (frontmatter + body)
2. **Research artifacts** — All files referenced in the idea file's `research: []` frontmatter array. Read full content of each. These ground the candidates in research findings rather than speculation.
3. **Persona guide** — `persona.md` — governs voice and word choice for candidate sentences. The format constraints (one sentence, numbered list) enforce brevity; the persona governs how that sentence reads.

Extract from the idea file:

- `stage` from frontmatter
- The `### Thought Outline` section content
- The `### Research Summary` section content
- The header fields (Core insight, Problem it addresses, Who cares, Strategic connection)

### Step 2: Validate

Confirm the idea file has:

- `stage` is `developing`, `drafting`, `refining`, or `complete`
- A `### Thought Outline` section exists and is non-empty

**If stage is `seed`:** Report "Idea '{name}' is at seed stage — develop it first with /develop before checking buildable surface." and exit.

**If Thought Outline is missing or empty:** Report "Idea '{name}' has no Thought Outline — cannot assess buildable surface without it." and exit.

### Step 3: Detect

Read the Thought Outline and apply the first principle from the agent persona: **Could a product team read this and know what to build in their first sprint?**

- **Feature-shaped (no-op):** The outline names a specific surface and commits to a single product approach. A team could start scoping. Skip to Step 6.
- **Principle-shaped (fire):** The outline describes a strategic direction but a team would still need to decide what to build. Proceed to Step 4.
- **Borderline (fire with flag):** You're genuinely uncertain. Proceed to Step 4, mark output as borderline.

State your classification and reasoning. No mechanical framework — apply product-strategy judgment.

### Step 4: Generate Candidates

Generate 3-5 genuinely distinct product approach candidates that could express the principle described in the Thought Outline.

**Grounding rule:** Each candidate must connect to a finding from the research artifacts or Research Summary. Do not speculate. If research is thin, generate fewer candidates (3 minimum) rather than ungrounded ones.

**Distinctness check:** After generating candidates, verify each pair is genuinely distinct:

- Different product approach (not different features on the same surface)
- Different interaction model or user action
- Different assumption about where value lives

If any two candidates are "the same thing but with X," merge or replace one.

**For each candidate, produce:**

- A candidate name (product noun — what is built)
- One sentence: the user action and what makes this approach distinct

### Step 5: Write Section

**Write the Buildable Surface section** into the idea file, placed between `### Thought Outline` and `### Open Questions`.

**Standalone invocation (not inline from /develop):** Check if a `### Buildable Surface` section already exists in the idea file.

- If it exists: present the existing section to the user and ask "Overwrite existing Buildable Surface section?" Wait for confirmation before proceeding. If user declines, present the new analysis without writing and exit.
- If it does not exist: write directly.

**Inline invocation (called from /develop Step 5c):** Write directly — the card was just written in the same session, so no user-modified content exists to protect.

To detect inline vs standalone: check if the idea file's `stage` was just changed to `developing` in this session (frontmatter `updated` is today's date AND stage is `developing`). If so, treat as inline. Otherwise, treat as standalone.

**Section format:**

```markdown
### Buildable Surface
1. [Candidate Name] — [One sentence: user action + what makes this approach distinct]
2. [Candidate Name] — [One sentence]
3. [Candidate Name] — [One sentence]
```

No sub-labels, no recommended surface, no rationale. The numbered list implies these are options to explore — the human and /draft pick which to develop. Appetite bounding happens downstream.

**Write constraints:**

- Insert between `### Thought Outline` and `### Open Questions` using Edit tool
- Do not write detection classification (borderline, principle-shaped) into the card — report it in terminal output only
- Do not modify any other section of the idea file
- Do not change frontmatter (stage, impact dimensions, etc.)

### Step 6: Present Results

**If no-op (feature-shaped):**

```text
Buildable surface check: {idea-name}

**Result:** No-op — feature-shaped

**Why:** {1-2 sentences — what makes this feature-shaped. What specific surface does the Thought Outline commit to?}
```

**If fired (principle-shaped or borderline):**

```text
Buildable surface check: {idea-name}

**Result:** {Principle-shaped | Borderline} — section generated

**Why:** {1-2 sentences — what makes this principle-shaped or borderline. What question would a product team still need to answer?}

**Approaches generated:**
1. {Candidate Name} — {summary}
2. {Candidate Name} — {summary}
3. {Candidate Name} — {summary}

**Section written to:** Ideas/{idea-name}.md (between Thought Outline and Open Questions)
```

## Stop Rules

| Condition | Action |
| ----------- | -------- |
| Idea file not found | Fuzzy match against Ideas/ listing. If no match, report available files and exit. |
| Idea at seed stage | Report: develop it first with /develop. Exit. |
| No Thought Outline | Report: cannot assess without Thought Outline. Exit. |
| All candidates fail grounding check (no research support) | Report: research too thin for grounded candidates. List what research would be needed. Exit without writing section. |
| User declines overwrite (standalone re-run) | Present new analysis without writing. Exit. |

## Error Handling Summary

| Condition | Behavior |
| ----------- | ---------- |
| No argument and no eligible ideas exist | Report "No developing-or-later ideas found in Ideas/" and exit |
| Idea file not found | Report with available filenames from Ideas/ listing, exit |
| Idea at seed stage | Report: develop first, exit |
| Thought Outline missing or empty | Report: cannot assess, exit |
| Research artifacts referenced but files not found | Log missing files, continue with available research. If zero research available, fire stop rule. |
| Idea file has malformed frontmatter | Report parsing issue with specifics, exit |
| Edit fails (section markers not found) | Report error, present analysis in output so work is not lost |
| Existing section found (standalone) | Prompt for overwrite confirmation |

## Scope Boundaries

This skill does NOT:

- Change the idea's stage
- Modify impact dimensions or other TL;DR sections (only inserts/replaces the Buildable Surface section)
- Generate divergent or creative angles (that's divergent-thinking)
- Assess market viability of candidates (that's edtech-sme)
- Assess pedagogical validity (that's educator-sme)
- Produce TAM estimates (that's tam-estimate)
- Work on seed-stage ideas (develop first)
- Read strategy docs or OKRs (works from card, research, and persona guide only)
