---
name: divergent-thinking
description: This skill should be used when the user asks to "think divergently about [idea]", "brainstorm angles for [idea/subject]", "nonlinear thinking on [idea/subject]", "explore creative connections for [idea/subject]", or "divergent analysis of [subject]". Generates 3-5 unexpected, nonlinear connections for a strategic idea OR an arbitrary subject by following structural pattern similarity across domains.
argument-hint: [idea-name]
context: fork
agent: divergent-thinking
disable-model-invocation: false
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Bash(date:*)
  - Bash(mkdir:*)
  - mcp__obsidian__read_note
  - mcp__obsidian__write_note
  - mcp__obsidian__update_frontmatter
---

# /divergent-thinking — Nonlinear Thinking Enrichment Agent

Generates 3-5 unexpected, nonlinear connections and extensions for a strategic idea. Works from the idea and general knowledge only — deliberately avoids strategy docs, market data, and research artifacts to prevent anchoring to existing frames.

This is an enrichment agent, not a stage transition workflow. It does not change the idea's stage.

## Invocation

```text
/divergent-thinking [idea-name]                # idea mode
/divergent-thinking --adhoc "subject string"   # ad-hoc mode
```

Two modes:

- **Idea mode** (naked argument): generates angles for an idea. Writes local artifact + updates idea frontmatter.
- **Ad-hoc mode** (`--adhoc "subject"`): generates angles for a free-form topic/concept. No local artifact, no frontmatter update.

Examples: `/divergent-thinking foraging-intelligence`, `/divergent-thinking --adhoc "authentic assessment at scale"`.

## Arguments

Parse `$ARGUMENTS` to determine mode:

- If `--adhoc "subject"` present: **ad-hoc mode**, subject = value of flag. Skip Ideas/ resolution.
- Otherwise: **idea mode**, naked argument = candidate idea name.

**Idea-mode resolution (fail-closed):**

| Input | Behavior |
| ------- | ---------- |
| Empty | Glob `Ideas/*.md`, present titles, ask user to select |
| `idea-name` or `idea-name.md` | Exact match at `Ideas/{arg}.md` (strip `.md` first) |
| No exact match | Case-insensitive substring match against all `Ideas/*.md` filenames |
| Single fuzzy match | Use it |
| Multiple fuzzy matches | Present options, ask user to pick |
| Zero matches | **ERROR**: "Idea file not found: `{arg}`. Closest candidates in Ideas/: `{list up to 5}`. For ad-hoc divergent thinking on a non-idea subject, use: `/divergent-thinking --adhoc \"{arg}\"`." Exit. Do NOT silently fall through to ad-hoc. |

## Persona

This skill runs in the divergent-thinking agent's context. The agent carries the nonlinear thinker persona, quality gate, coverage checks, and voice requirements. See `.claude/agents/divergent-thinking.md`.

**Invocation note:** When executed by a pointer-invoked agent rather than the Skill tool: generic Read/Write/Edit on vault .md files may be redirected — use the Obsidian MCP equivalents.

## Execution Flow

Execute these steps in order. Stop and report errors at any step rather than continuing with bad data.

### Step 0: Parse Arguments

1. Read `$ARGUMENTS`. Detect `--adhoc` flag.
2. **If `--adhoc "subject"` is present:** mode = `ad-hoc`, subject = value of flag. Skip Ideas/ resolution.
3. **Otherwise (idea mode):**
   - If empty: `Glob` `Ideas/*.md`, read first 20 lines for title and stage, present all ideas, ask user to select. If none exist, exit.
   - Try exact match at `Ideas/{argument}.md` (strip `.md` first)
   - If no exact match, case-insensitive substring match
   - Single fuzzy match → use it
   - Multiple fuzzy matches → present options, ask user to pick
   - Zero matches → **ERROR**: "Idea file not found: `{argument}`. Closest candidates in Ideas/: `{list up to 5}`. For ad-hoc divergent thinking, use: `/divergent-thinking --adhoc \"{argument}\"`." Exit. Do NOT silently fall through to ad-hoc.

### Step 1: Load Context

**Idea mode:** Load only the idea file at the resolved path — full content (frontmatter + body). Extract:

- Core insight
- Themes (from frontmatter `themes: []`)
- Domain (from frontmatter `domain:`)
- Current stage (from frontmatter `stage:`)
- Any existing body content relevant to understanding the idea

**Ad-hoc mode:** The subject string is the seed for divergent thinking. No idea file, no themes, no domain. The subject itself is the core insight.

Both modes: Do NOT load any other files. No persona guide, no strategy docs, no OKRs, no other ideas, no research artifacts. Loading more anchors thinking to existing frames.

### Step 2: Validate

Confirm the idea file has:

- A core insight populated in the body (non-empty)
- `domain` set in frontmatter
- `themes` with at least one entry in frontmatter

**If the idea is too vague** (core insight is a single vague phrase with no specificity, or themes are generic like `[misc]`): Report "Idea '{name}' is too vague for meaningful divergent thinking. The core insight needs to be specific enough to generate structural analogies. Please sharpen the core insight and try again." and exit.

### Step 3: Generate Angles

Let the idea's core structure — not its surface domain — drive association. Follow the structural pattern wherever it leads. Generate 3-5 angles total.

Apply your quality gate to every angle. Run your coverage check after connections emerge to verify you haven't been one-dimensional. If the idea is a weak seed, apply your creative rescue behavior. For `domain: platform` ideas, apply your platform-domain handling.

### Step 4: Identify the Disruptive One

Of the 3-5 angles generated, identify which one has the highest potential to fundamentally reframe the opportunity. This is the angle that, if taken seriously, would change what problem the team thinks they are solving. One sentence explaining why.

### Step 5: Write Research Artifact

**Ad-hoc mode:** Skip this step — no idea-scoped folder, no frontmatter to update. Jump to Step 6 with angles presented in conversation only.

**Idea mode:**

1. Get today's date using `Bash(date:*)`: `date +%Y-%m-%d`
2. Determine the idea name from the filename (strip `.md` extension)
3. Create directory if needed: `Research/{idea-name}/`
4. Write `Research/{idea-name}/divergent-angles.md`. If a file already exists at that path from a prior run, write to `Research/{idea-name}/divergent-angles-{YYYY-MM-DD}.md` instead; if that also exists, append `-2`, `-3`, etc. Use this structure:

```markdown
---
type: incubator/research
idea: "{idea-name}"
agent: divergent-thinking
created: {today's date YYYY-MM-DD}
---

# Divergent Thinking: {Idea Title}

**Idea:** {core insight from idea file}
**Generated:** {today's date}

---

## Angles

### [Provocative Title 1]
**The connection:** [2-3 sentences — source domain, structural parallel, why it matters]
**What it opens up:** [1-2 sentences — capabilities, positions, or advantages]
**Strategic thread:** [One sentence connecting to your organization]

### [Provocative Title 2]
**The connection:** [2-3 sentences]
**What it opens up:** [1-2 sentences]
**Strategic thread:** [One sentence]

{...repeat for each angle, 3-5 total}

---

## The Disruptive One

**[Title of the chosen angle]**

[One sentence — why this angle has the highest potential to fundamentally reframe the opportunity.]

---

## Connection Map

| Angle | Lens Used | Capability Link |
|-------|-----------|-----------------|
| [Title 1] | [Which lens] | [Specific product/capability] |
| [Title 2] | [Which lens] | [Specific product/capability] |
{...}
```

1. Update the idea file frontmatter: append the research artifact path to the `research: []` array.

**Frontmatter update rules:**

- The path to append is the file actually written in step 4 (may include dated suffix if it's an augment run)
- If `research:` is currently `[]` (empty array), replace with `[{written path}]`
- If `research:` already contains entries, append the new path to the existing array
- Do NOT remove older dated-suffix entries from prior runs — augment artifacts coexist
- Update `updated:` to today's date
- Do NOT change the `stage:` field — this agent does not transition stages

### Step 6: Present Results

Present the completed analysis to the user with:

```text
Divergent thinking complete: {idea-name}

**Angles generated:** {N}

{For each angle:}
- **{Provocative Title}** — {one-sentence summary of the connection}

**The disruptive one: {Title}**
{One sentence why}

**Capability connections:**
{List which angles connect to specific products/capabilities}

**Research artifact:** Research/{idea-name}/divergent-angles.md
**Idea frontmatter updated:** research array now includes divergent-angles.md
```

## Stop Rules

| Condition | Action |
| ----------- | -------- |
| Idea file not found | Fuzzy match against Ideas/ listing. If no match, report available files and exit. |
| Idea too vague | Report: core insight too abstract for structural analogies. Ask human to sharpen it. |
| Research directory creation fails | Report error, exit. |
| All generated angles fail both quality tests | Report that divergent thinking did not produce viable angles for this idea. Present the best attempt anyway with explicit notes on which test each angle fails. |

## Error Handling Summary

| Condition | Behavior |
| ----------- | ---------- |
| No argument and no ideas exist | Report "No ideas found in Ideas/" and exit |
| Idea file not found | Report with available filenames from Ideas/ listing, exit |
| Idea has no core insight | Report "Core insight missing — cannot generate angles without a seed to diverge from" and exit |
| Idea has no themes or domain | Report specific missing fields and exit |
| Idea too vague for meaningful angles | Report and ask human to sharpen the core insight |
| Idea file has malformed frontmatter | Report parsing issue with specifics, exit |
| Research directory already exists | Continue (write/overwrite divergent-angles.md in it) |
| divergent-angles.md already exists for this idea | Write dated-suffix augment file per Step 5 (`divergent-angles-{YYYY-MM-DD}.md`, counter for same-day); append new path to frontmatter; do not remove the original |
| Frontmatter research array update fails | Report error, present angles in output anyway so work is not lost |

## Scope Boundaries

This skill does NOT:

- Change the idea's stage
- Modify the idea body content (only updates frontmatter `research:` and `updated:` fields)
