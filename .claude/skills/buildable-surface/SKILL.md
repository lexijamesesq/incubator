---
name: buildable-surface
description: This skill should be used when the user asks to "check buildable surface for [idea]", "generate feature candidates for [idea]", "buildable surface [idea]", "what could we build for [idea]", or "surface candidates for [idea]". Detects principle-shaped Thought Outlines and generates distinct product approach candidates. No-ops on feature-shaped ideas.
argument-hint: "[idea-name | idea-row-url] [notion_ideas=...] [notion_config=...] [persona_file=...]"
context: fork
agent: buildable-surface
disable-model-invocation: false
allowed-tools:
  - Read
  - Skill
  - Bash(date:*)
  - mcp__notion__notion-fetch
  - mcp__notion__notion-query-data-sources
  - mcp__notion__notion-update-page
---

# /buildable-surface — Buildable Surface Enrichment Agent

Detects whether a developed idea's Thought Outline describes a strategic principle (principle-shaped) or a specific buildable capability (feature-shaped). For principle-shaped ideas, generates 3-5 distinct product approach candidates. For feature-shaped ideas, no-ops.

This is an enrichment agent, not a stage transition workflow. It does not change the idea's stage.

## Invocation

```text
/buildable-surface [idea-name]
```

- Required argument: the name of a developing-or-later idea (its Slug in the Ideas database), or the idea row's URL when another skill invokes this one
- Works on ideas at developing, drafting, refining, or complete stages (must have a Thought Outline)
- Examples: `/buildable-surface foraging-intelligence`, `/buildable-surface cache-optimization`

**Idea-only by design.** This skill has no `--adhoc` mode. Its value proposition is classifying an idea's Thought Outline as principle-shaped vs. feature-shaped — an idea-shape question that has no analogue when run against a free-form subject. The other five enrichment skills (edtech-sme, educator-sme, divergent-thinking, tam-estimate, cross-domain) support `--adhoc`; buildable-surface intentionally does not.

## Where Things Are

Ideas, research, output documents and configuration live in Notion. How a skill reads and writes them is stated once, in `reference/skill-conventions-notion-access.md`: read it before the first step and follow it. Only what is specific to this skill is stated here.

- **Pointers:** `notion_ideas`, `notion_config`.
- **Rows it touches:** reads the idea row and every row in its Research relation; adds the `### Buildable Surface` section to the idea row's body. It changes no field.
- **Configuration keys:** `persona_skill`.

## Arguments

Parse `$ARGUMENTS` to resolve the target idea row: the first token that is not `key=value` names the idea; every `key=value` token is an override (`notion_ideas=`, `notion_config=`, `persona_file=`).

**Resolution rules:**

| Input | Behavior |
| ------- | ---------- |
| Empty | List all developing-or-later ideas in the Ideas view, ask user to select |
| A Notion row URL | The idea row, as `/develop` passes it. Fetch it and use it. |
| `idea-name` | Resolve to the Ideas row whose Slug is `idea-name` |
| `idea-name.md` | Strip `.md`, resolve as above |

**Fuzzy matching:** If exact match fails, find the rows whose Slug or Name contains the argument as a substring (case-insensitive). If exactly one match, use it. If multiple matches, present options and ask user to pick. If zero matches, report and exit.

## Persona

This skill runs in the buildable-surface agent's context. The agent carries the product strategist persona, detection heuristic, candidate quality standards, and appetite bounding framework. See `.claude/agents/buildable-surface.md`.

## Execution Flow

Execute these steps in order. Stop and report errors at any step rather than continuing with bad data.

### Step 0: Parse Arguments

1. Read `$ARGUMENTS`
2. Settle the pointers: an override where one is given, the `CLAUDE.md` front matter otherwise.
3. If empty: read the Ideas view and check each row's Stage field. Present ideas at developing or later stages (developing, drafting, refining, complete) to the user and ask them to select one. If none exist, report "No developing-or-later ideas found in the Ideas database" and exit.
4. If a Notion row URL is provided: fetch it. If the database it is in is not `notion_ideas`, report and exit.
5. If a name is provided: read the Ideas view and resolve it against the Slug field
   - Try exact match first (with and without `.md` extension)
   - If not found, try fuzzy substring match against the Slug and Name of all rows
   - If exactly one fuzzy match, use it
   - If multiple fuzzy matches, present options and ask user to pick
   - If zero matches, report "Idea not found: {argument}. Available ideas: {list of slugs}" and exit

### Step 1: Load Context

Fetch the idea row first (unless Step 0 already did), then load the rest in parallel:

1. **Idea row** — one fetch returns the full content (fields + body)
2. **Research artifacts** — Every row in the idea row's `Research` relation. Fetch each and read its full body. These ground the candidates in research findings rather than speculation.
3. **Persona guide** — fetch the `notion_config` page, read `persona_skill`, and load that skill with the Skill tool. If `persona_file=` was passed, Read that file instead; if its content is only a pointer elsewhere, refuse it with the conventions' message and exit. The persona governs voice and word choice for candidate sentences. The format constraints (one sentence, numbered list) enforce brevity; the persona governs how that sentence reads.

Extract from the idea row:

- `Stage` from the fields
- The `### Thought Outline` section content
- The `### Research Summary` section content
- The header fields (Core insight, Problem it addresses, Who cares, Strategic connection)

### Step 2: Validate

Confirm the idea row has:

- `Stage` is `developing`, `drafting`, `refining`, or `complete`
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

**Write the Buildable Surface section** into the idea row's body, placed between `### Thought Outline` and `### Open Questions`.

**Standalone invocation (not inline from /develop):** Check if a `### Buildable Surface` section already exists in the card.

- If it exists: present the existing section to the user and ask "Overwrite existing Buildable Surface section?" Wait for confirmation before proceeding. If user declines, present the new analysis without writing and exit.
- If it does not exist: write directly.

**Inline invocation (called from /develop Step 5c):** Write directly — the card was just written in the same session, so no user-modified content exists to protect.

To detect inline vs standalone: check if the idea's stage was just changed to `developing` in this session (the row's `Updated` field is today's date, the local date from `date +%Y-%m-%d`, AND `Stage` is `developing`). If so, treat as inline. Otherwise, treat as standalone.

**Section format:**

```markdown
### Buildable Surface
1. [Candidate Name] — [One sentence: user action + what makes this approach distinct]
2. [Candidate Name] — [One sentence]
3. [Candidate Name] — [One sentence]
```

No sub-labels, no recommended surface, no rationale. The numbered list implies these are options to explore — the human and /draft pick which to develop. Appetite bounding happens downstream.

**Write constraints:**

- Insert between `### Thought Outline` and `### Open Questions` with one `notion-update-page` `update_content` call on the idea row, working from the body as fetched: the operation's `old_str` is the `### Open Questions` heading line as fetched, and its `new_str` is the `### Buildable Surface` heading, a blank line, the numbered list, a blank line, then that same `### Open Questions` heading.
- Overwriting an existing section (standalone, confirmed): in the same call, one operation per existing candidate line with that line as `old_str` and an empty `new_str`, and one operation replacing the `### Buildable Surface` heading line with the heading, a blank line and the new list. Do not touch `### Open Questions` in that case.
- Never put the `### Original Capture` heading or anything below it in an `old_str` or a `new_str`.
- If an operation matched nothing — a warning when other operations matched, a failed call when none did — fetch the row again and repeat that operation with text from the fresh fetch.
- Do not write detection classification (borderline, principle-shaped) into the card — report it in terminal output only
- Do not modify any other section of the card
- Do not change any field (Stage, impact dimensions, etc.)

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

**Section written to:** {URL of the idea row} (between Thought Outline and Open Questions)
```

## Stop Rules

| Condition | Action |
| ----------- | -------- |
| Idea not found | Fuzzy match against the Ideas view. If no match, report available slugs and exit. |
| Idea at seed stage | Report: develop it first with /develop. Exit. |
| No Thought Outline | Report: cannot assess without Thought Outline. Exit. |
| All candidates fail grounding check (no research support) | Report: research too thin for grounded candidates. List what research would be needed. Exit without writing section. |
| User declines overwrite (standalone re-run) | Present new analysis without writing. Exit. |

## Error Handling Summary

| Condition | Behavior |
| ----------- | ---------- |
| No argument and no eligible ideas exist | Report "No developing-or-later ideas found in the Ideas database" and exit |
| Idea not found | Report with available slugs from the Ideas view, exit |
| Idea at seed stage | Report: develop first, exit |
| Thought Outline missing or empty | Report: cannot assess, exit |
| Research rows related but cannot be fetched | Log the missing rows, continue with available research. If zero research available, fire stop rule. |
| Idea row cannot be read, or its fields are missing | Report the issue with specifics, exit |
| `persona_file=` holds only a pointer elsewhere | Refuse it with the conventions' message, exit |
| Card update fails (section headings not found) | Report error, present analysis in output so work is not lost |
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
