---
name: refine-seed
description: This skill should be used when the user asks to "refine a seed", "prep [idea] for development", "refine-seed [idea]", "clarify [idea]", or "get [idea] ready for /develop". Interprets a raw seed's intent, drafts header fields, determines capability-vs-experience framing, surfaces related ideas, and aligns with the human before /develop runs.
argument-hint: [idea-name]
context: conversation
disable-model-invocation: false
allowed-tools:
  - Read
  - Edit
  - Glob
  - Grep
  - Bash(date:*)
---

# /refine-seed — Seed Intent Refinement (Pre-Development)

Prepares a raw or loosely-structured seed for development by interpreting its intent, drafting header fields, surfacing related ideas, and aligning with the human. This is the interactive step where the human and model agree on what the seed means before /develop runs.

Runs AFTER the router creates a seed (Stage 0→1) and BEFORE /develop transforms it (Stage 1→2). The seed may arrive with just frontmatter + Original Capture (from the router), or with draft header fields that need refinement (from manual creation or an earlier router version).

## Invocation

```text
/refine-seed [idea-name]
```

- Required argument: a seed-stage idea file in `Ideas/`
- If no argument: list seed-stage ideas for selection
- Examples: `/refine-seed foraging-intelligence`, `/refine-seed cache-optimization`

## Arguments

Parse `$ARGUMENTS` to resolve the target idea file.

| Input | Behavior |
| ------- | ---------- |
| Empty | List all seed-stage ideas in Ideas/, ask user to select |
| `idea-name` | Resolve to `Ideas/{idea-name}.md` |
| `idea-name.md` | Strip `.md`, resolve as above |

Fuzzy matching: if exact match fails, try substring match. One match: use it. Multiple: present options. Zero: report and exit.

## Reference Material

`incubator-reference.md` is a thin section index. Load only the `reference/` section files this skill needs:

- `reference/stage-model.md` — seed-stage semantics
- `reference/frontmatter-schema.md` — domain, themes, related-ideas fields
- `reference/templates.md` — Seed Template (validation) and TL;DR header fields (drafting)
- `reference/architecture.md` — related-idea consolidation and merge mechanics

## Execution Flow

### Step 1: Load Context

Load in parallel:

1. **Seed file** at the resolved path — full content
2. **Portfolio index** — Use `Glob` to list all `.md` files in `Ideas/`, then apply tiered reading:
   - **Complete-stage ideas:** Read frontmatter only (first 25 lines or until `---` closes). Extract: stage, themes, domain.
   - **All other stages:** Read until first `###` heading or 40 lines. Extract: frontmatter + header fields.
   From the loaded index, extract the **portfolio theme vocabulary** (all unique themes values).
3. **Persona guide** — `persona.md` (voice calibration for drafted fields)

### Step 2: Validate

Confirm:

- `stage: seed` in frontmatter
- `### Original Capture` section exists and is non-empty
- `domain` and at least one `themes` entry set in frontmatter

If Original Capture is missing: report and exit. There's nothing to interpret without the raw capture.

If domain/themes missing: note for the human but continue — refinement can propose these.

### Step 3: Interpret the Seed

Read the Original Capture carefully. This is the raw thought — it contains the idea's actual intent, which may differ from any draft header fields already present.

#### 3a: Determine the idea's nature

Ask: **Does this seed describe something that doesn't exist yet, or something that exists but works poorly?**

- **Capability-absent:** The platform cannot do this at all. The gap is foundational — the capability must be built before any experience can be designed around it. Indicators: "doesn't exist," "can't do," "no way to," "not possible today."
- **Experience-broken:** The platform can do this, but the experience is wrong — confusing, inefficient, or missing key workflow elements. Indicators: "frustrating," "workaround," "defect to other tools," "not designed for."
- **Hybrid:** The platform has partial capability but the gap is both functional and experiential. Both dimensions need representation.

This classification shapes how the header fields are drafted — capability-absent ideas lead with the gap, experience-broken ideas lead with the user's moment, hybrids name both.

##### 3b: Draft header fields

Using the Original Capture and the nature classification, draft:

- **Core insight** — One sentence. For capability-absent: name the capability gap through what users can't do. For experience-broken: name the broken moment through what users encounter. For hybrid: lead with whichever is more fundamental, acknowledge the other.
- **Source** — Where this came from. If the seed has a Source field, preserve it. If not, infer from context (inbox, conversation, gap analysis, etc.).
- **Initial strategic connection** — One sentence naming an organizational priority and the mechanism. Capability-absent seeds connect to priorities about building/expanding capability. Experience-broken seeds connect to priorities about improving/optimizing experience. Do not connect a capability-absent seed to an experience-optimization priority or vice versa — that's the conflicting-signal problem this step exists to prevent.

**Voice:** Header fields follow `persona.md` — confident, declarative, specific, no hedging.

### Step 4: Surface Related Ideas

Using the portfolio index from Step 1, find related ideas at **seed, developing, drafting, or refining** stages. **Exclude complete-stage ideas** from merge/keep — they are finished work.

**Match criteria** — an idea is "related" if:

- It shares 2+ themes from the `themes` frontmatter array, OR
- It addresses the same strategic connection or organizational priority

**If related ideas found**, present with merge/keep recommendations:

**Merge signals** (recommend merge when most present):

- Core insights converge — same idea, different framing
- Who-cares overlaps significantly
- One is a clear subset of the other

**Keep-separate signals** (recommend keep-separate when any present):

- Distinct who-cares — different audiences or needs
- Distinct problems — independently justifiable decisions
- Each delivers customer value independently

**Stage-aware actions:**

| Related idea stage | Available actions |
| --- | --- |
| **Seed** | Merge into one seed (human picks primary), or keep separate |
| **Developing** | Keep separate; note relationship for differentiation |
| **Drafting / Refining** | Keep separate; note relationship |

Present:

> **Related ideas:** {N} found
>
> | Idea | Stage | Action | Why |
> | --- | --- | --- | --- |
> | {name} | {stage} | {Merge / Add to related-ideas / No action} | {rationale} |
>
> **Unique territory for this seed:** {one sentence — what this idea does that no sibling addresses}

**Complete-stage reference:** If any complete ideas match, note them as context only:
> **Reference (completed work):** {name} — {relevance}

Wait for human decision on merge/keep and related-ideas updates before proceeding.

**Relationship write-back:** After human confirms, update `related-ideas` frontmatter on all affected cards.

**Merge mechanics** (when human says merge): Follow the same protocol as the current /develop Step 3 — primary selection, frontmatter merge, body merge with dual Original Captures, secondary archived.

### Step 5: Present Refined Seed

Present the complete refined seed to the human:

```text
Seed refinement: {idea-name}

**Nature:** {Capability-absent | Experience-broken | Hybrid}
**Rationale:** {One sentence — why this classification}

**Drafted fields:**
- **Core insight:** {drafted}
- **Source:** {drafted or preserved}
- **Strategic connection:** {drafted}

**Related ideas:** {summary from Step 4}
**Unique territory:** {from Step 4}

**Theme check:**
- Current: [{themes}]
- Suggested changes: {add/remove with rationale, or "no changes"}

Ready to write? Or adjust any fields first?
```

The human may:

- Accept as-is → write and done
- Modify any field → update and re-present
- Disagree with the nature classification → adjust framing and re-draft
- Request more context → discuss before committing

This is the alignment step. Take the time to get it right — /develop depends on coherent signals.

### Step 6: Write Refined Seed

After human approval, update the idea file:

**Frontmatter updates:**

- `updated: {today's date}`
- `themes: []` — updated per theme check
- `related-ideas: []` — updated per Step 4
- Any other frontmatter adjustments agreed with human

**Body update:** Write the header fields above Original Capture:

```markdown
## [Idea Title]

**Core insight:** {approved}
**Source:** {approved}
**Initial strategic connection:** {approved}

### Original Capture
{preserved verbatim}
```

Report: "Seed refined: {idea-name}. Ready for /develop."

## Stop Rules

| Condition | Action |
| ----------- | -------- |
| No Original Capture | Cannot refine — nothing to interpret. Exit. |
| Idea not at seed stage | Report current stage. Exit. |
| Seed is a clear duplicate of an existing idea | Present the duplicate, recommend merge or archive. Wait for human. |
| Core insight too vague to draft after reading capture | Ask the human: "What's the one-sentence version of this idea?" Use their answer. |

## Error Handling

| Condition | Behavior |
| ----------- | ---------- |
| No argument and no seed-stage ideas | Report and exit |
| Idea file not found | Fuzzy match, report available files, exit |
| Idea not at seed stage | Report current stage, exit |
| Malformed frontmatter | Report specific issue, exit |
| Related idea file malformed | Log, continue with valid files |

## Scope Boundaries

This skill does NOT:

- Conduct research (that's /develop's job)
- Assess impact dimensions (that's the synthesis agent's job)
- Draft output documents (that's /draft's job)
- Classify or route inbox items (that's the router's job)
- Develop the seed beyond header fields (Core insight, Source, Strategic connection + related ideas)
- Change the seed's stage (it stays at `seed` — /develop changes it to `developing`)
- Make merge decisions autonomously (always presents to human)
