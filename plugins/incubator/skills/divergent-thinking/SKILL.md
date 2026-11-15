---
name: divergent-thinking
description: This skill should be used when the user asks to "think divergently about [idea]", "brainstorm angles for [idea/subject]", "nonlinear thinking on [idea/subject]", "explore creative connections for [idea/subject]", or "divergent analysis of [subject]". Generates 3-5 unexpected, nonlinear connections for a strategic idea OR an arbitrary subject by following structural pattern similarity across domains.
argument-hint: "[idea-name | idea-row-url | --adhoc \"subject\"] [notion_ideas=...] [notion_research=...]"
context: fork
agent: incubator:divergent-thinking
disable-model-invocation: false
allowed-tools:
  - Read
  - Bash(date:*)
  - mcp__notion__notion-fetch
  - mcp__notion__notion-query-data-sources
  - mcp__notion__notion-create-pages
  - mcp__notion__notion-update-page
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

- **Idea mode** (naked argument — an idea's Slug, or the idea row's URL): generates angles for an idea. Writes its artifact as a row in the Research database (Research type `divergent-angles`), related to the idea; that relation is what puts it on the idea's research list.
- **Ad-hoc mode** (`--adhoc "subject"`): generates angles for a free-form topic/concept. No artifact row, nothing written to Notion.

Examples: `/divergent-thinking foraging-intelligence`, `/divergent-thinking --adhoc "what a school learns about a student who arrives mid-year"`.

## Where Things Are (idea mode)

Ad-hoc mode makes no Notion call. Idea mode reads and writes Notion, and how a skill does that is stated once, in `reference/skill-conventions-notion-access.md` in the Incubator repo: read it before Step 0 and follow it. If idea mode cannot read that file (the session is not in the Incubator repo and has no copy), stop and say so. Only what is specific to this skill is stated here.

- **Pointers (idea mode):** `notion_ideas`, `notion_research`. A caller that has already fetched the Research database may pass `research_data_source=<collection:// URL>`. A pointer idea mode needs and does not have: report "Idea mode needs the {pointer} pointer (CLAUDE.md front matter, or a {pointer}= argument). For a subject that is not an idea, use --adhoc." and exit.
- **Rows it touches (idea mode):** reads the idea row; creates one Research row related to it, Research type `divergent-angles`; sets the idea row's `Updated`.

## Arguments

Parse `$ARGUMENTS` to determine mode. Every `key=value` token (`notion_ideas=`, `notion_research=`) is a pointer override, not the idea:

- If `--adhoc "subject"` present: **ad-hoc mode**, subject = value of flag. Skip idea resolution.
- Otherwise: **idea mode**, naked argument = candidate idea name, or the idea row's URL.

**Idea-mode resolution (fail-closed):**

| Input | Behavior |
| ------- | ---------- |
| Empty | Read the Ideas view, present the titles of the rows not at Stage `archived`, ask user to select |
| A Notion row URL | The idea row, as `/develop` and other skills pass it. Fetch it; do not read the Ideas view. |
| `idea-name` or `idea-name.md` | Exact match on the Slug field (strip `.md` first) |
| No exact match | Case-insensitive substring match against the Slug and Name of all rows |
| Single fuzzy match | Use it |
| Multiple fuzzy matches | Present options, ask user to pick |
| Zero matches | **ERROR**: "Idea not found: `{arg}`. Closest candidates in the Ideas database: `{list up to 5 slugs}`. For ad-hoc divergent thinking on a non-idea subject, use: `/divergent-thinking --adhoc \"{arg}\"`." Exit. Do NOT silently fall through to ad-hoc. |

## Persona

This skill runs in the divergent-thinking agent's context. The agent carries the nonlinear thinker persona, quality gate, coverage checks, and voice requirements. See `.claude/agents/divergent-thinking.md`.

## Execution Flow

Execute these steps in order. Stop and report errors at any step rather than continuing with bad data.

### Step 0: Parse Arguments

1. Read `$ARGUMENTS`. Detect `--adhoc` flag.
2. **If `--adhoc "subject"` is present:** mode = `ad-hoc`, subject = value of flag. Skip idea resolution.
3. **Otherwise (idea mode):** settle the pointers (an argument override where one is given, the `CLAUDE.md` front matter otherwise), then:
   - If the argument is a Notion row URL: fetch it and use it. If the database it is in is not `notion_ideas`, report and exit.
   - If empty: read the Ideas view for Name and Stage, present all ideas, ask user to select Leave out rows at Stage `archived`. If none exist, exit.
   - Try exact match on the Slug field (strip `.md` first)
   - If no exact match, case-insensitive substring match against the Slug and Name of all rows
   - Single fuzzy match → use it
   - Multiple fuzzy matches → present options, ask user to pick
   - Zero matches → **ERROR**: "Idea not found: `{argument}`. Closest candidates in the Ideas database: `{list up to 5}`. For ad-hoc divergent thinking, use: `/divergent-thinking --adhoc \"{argument}\"`." Exit. Do NOT silently fall through to ad-hoc.

### Step 1: Load Context

**Idea mode:** Load only the idea row — one fetch (unless Step 0 already did) returns the full content (fields + body). Extract:

- Core insight
- Themes (from the `Themes` field)
- Domain (from the `Domain` field)
- Current stage (from the `Stage` field)
- Any existing body content relevant to understanding the idea

**Ad-hoc mode:** The subject string is the seed for divergent thinking. No idea row, no themes, no domain. The subject itself is the core insight.

Both modes: Do NOT load anything else. No persona guide, no strategy docs, no OKRs, no other idea rows, no research rows (the idea's `Research` relation lists them; do not fetch them). Loading more anchors thinking to existing frames.

### Step 2: Validate

Confirm the idea row has:

- A core insight populated in the body (non-empty)
- `Domain` set
- `Themes` with at least one entry

**If the idea is too vague** (core insight is a single vague phrase with no specificity, or themes are generic like `[misc]`): Report "Idea '{name}' is too vague for meaningful divergent thinking. The core insight needs to be specific enough to generate structural analogies. Please sharpen the core insight and try again." and exit.

### Step 3: Generate Angles

Let the idea's core structure — not its surface domain — drive association. Follow the structural pattern wherever it leads. Generate 3-5 angles total.

Apply your quality gate to every angle. Run your coverage check after connections emerge to verify you haven't been one-dimensional. If the idea is a weak seed, apply your creative rescue behavior. For `domain: platform` ideas, apply your platform-domain handling.

### Step 4: Identify the Disruptive One

Of the 3-5 angles generated, identify which one has the highest potential to fundamentally reframe the opportunity. This is the angle that, if taken seriously, would change what problem the team thinks they are solving. One sentence explaining why.

### Step 5: Write Research Artifact

**Ad-hoc mode:** Skip this step — there is no idea to relate an artifact to. Jump to Step 6 with angles presented in conversation only.

**Idea mode:**

1. Get today's date using `Bash(date:*)`: `date +%Y-%m-%d` (the local date)
2. The idea name is the row's Slug; the idea title is the row's Name
3. Create the artifact as a new row in the Research database with one `notion-create-pages` call (`allow_async` false, so the row's URL comes back). A row of this type may already exist for the idea from a prior run: do not look for it and do not change it. Every run creates a new row dated today, and earlier rows stay. Row parent: the Research data source — the `collection://` URL passed as `research_data_source=` when a caller gave one; otherwise fetch the `notion_research` database and take the data source it lists.
4. Row fields (these replace the artifact file's front matter), then the body structure:

| Field | Value |
| --- | --- |
| `Name` | `Divergent Thinking: {Idea Title}` |
| `Idea` | a one-item array holding the idea row's URL |
| `Research type` | `divergent-angles` |
| `Agent` | `divergent-thinking` |
| `date:Created:start` | today, `YYYY-MM-DD` (with `date:Created:is_datetime` 0) |

Never write a value outside a field's options. If Notion refuses the create because a field lacks the option, report which option is missing and present the angles in the output; do not create the row under another value.

The row body (the artifact; its title is the row's Name and is not repeated):

```markdown
**Idea:** {core insight from the idea row}
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

1. Update the idea row: the artifact joins its research list, and its `Updated` date moves to today.

**Idea-row update rules:**

- The research list is the idea row's `Research` relation. Setting `Idea` on the row created in step 3 is what adds the artifact to it; make no separate write for it
- Do not remove or change earlier rows of this type from prior runs — they coexist
- Set the idea row's `Updated` field to today's date with one `notion-update-page` `update_properties` call (`date:Updated:start` = today, `date:Updated:is_datetime` = 0). When the caller's contract says to hold back writes to the idea row (as `/develop` does), skip this call and say so in the report
- Do NOT change the `Stage` field — this agent does not transition stages

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

**Research artifact:** {URL of the artifact row}
**Idea row updated:** the Research relation now includes the divergent-angles row
```

## Stop Rules

| Condition | Action |
| ----------- | -------- |
| Idea not found | Fuzzy match against the Ideas view. If no match, report available slugs and exit. |
| Idea too vague | Report: core insight too abstract for structural analogies. Ask human to sharpen it. |
| Artifact row creation fails | Report error, present the angles in the output so the work is not lost, exit. |
| All generated angles fail both quality tests | Report that divergent thinking did not produce viable angles for this idea. Present the best attempt anyway with explicit notes on which test each angle fails. |

## Error Handling Summary

| Condition | Behavior |
| ----------- | ---------- |
| No argument and no ideas exist | Report "No ideas found in the Ideas database" and exit |
| Idea not found | Report with available slugs from the Ideas view, exit |
| Idea mode with a pointer missing | Report which pointer is missing and that `--adhoc` needs none, exit |
| Idea has no core insight | Report "Core insight missing — cannot generate angles without a seed to diverge from" and exit |
| Idea has no themes or domain | Report specific missing fields and exit |
| Idea too vague for meaningful angles | Report and ask human to sharpen the core insight |
| Idea row cannot be read | Report the issue with specifics, exit |
| A divergent-angles row already exists for this idea | Create a new row dated today per Step 5; it joins the idea's Research relation; do not change or remove the earlier row |
| The created row does not show the idea in its `Idea` relation, or the `Updated` write fails | Report error, present angles in output anyway so work is not lost |

## Scope Boundaries

This skill does NOT:

- Change the idea's stage
- Modify the idea body content (only the `Research` relation, through the new artifact row, and the `Updated` field change)
