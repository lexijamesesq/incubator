---
name: refine-seed
description: This skill should be used when the user asks to "refine a seed", "prep [idea] for development", "refine-seed [idea]", "clarify [idea]", or "get [idea] ready for /develop". Interprets a raw seed's intent, drafts header fields, determines capability-vs-experience framing, surfaces related ideas, and aligns with the human before /develop runs.
argument-hint: "[idea-name] [notion_ideas=...] [notion_config=...] [persona_file=...]"
context: conversation
disable-model-invocation: false
allowed-tools:
  - Read
  - Skill
  - Bash(date:*)
  - mcp__notion__notion-fetch
  - mcp__notion__notion-query-data-sources
  - mcp__notion__notion-update-page
---

# /refine-seed — Seed Intent Refinement (Pre-Development)

Prepares a raw or loosely-structured seed for development by interpreting its intent, drafting header fields, surfacing related ideas, and aligning with the human. This is the interactive step where the human and model agree on what the seed means before /develop runs.

Runs AFTER the router creates a seed (Stage 0→1) and BEFORE /develop transforms it (Stage 1→2). The seed may arrive with just its fields + Original Capture (from the router), or with draft header fields that need refinement (from manual creation or an earlier router version).

## Invocation

```text
/refine-seed [idea-name]
```

- Required argument: a seed-stage idea (its Slug in the Ideas database)
- If no argument: list seed-stage ideas for selection
- Examples: `/refine-seed foraging-intelligence`, `/refine-seed cache-optimization`

## Where Things Are

Ideas, research, output documents and configuration live in Notion. How a skill reads and writes them is stated once, in `reference/skill-conventions-notion-access.md`: read it before the first step and follow it. Only what is specific to this skill is stated here.

- **Pointers:** `notion_ideas`, `notion_config`.
- **Rows it touches:** reads the whole Ideas view once (name resolution and the portfolio index) and the idea row; writes the idea row's body above `### Original Capture` and its `Updated`, `Themes` and `Related ideas` fields; sets `Related ideas` on the rows it relates to; on a merge, writes the primary seed and sets the secondary's Stage to `archived`, and from then on writes only the primary.
- **Configuration keys:** `persona_skill`.

## Arguments

Parse `$ARGUMENTS` to resolve the target idea. The first token that is not `key=value` names the idea; every `key=value` token is a pointer override or `persona_file=<path>`.

| Input | Behavior |
| ------- | ---------- |
| Empty | Read the Ideas database, list the rows at Stage `seed`, ask user to select |
| `idea-name` | Resolve to the Ideas row whose Slug is `idea-name` |
| `idea-name.md` | Strip `.md`, resolve as above |
| A Notion page URL | Use that row directly (this is how another skill, such as /revert-to-seed, passes the idea) |

Fuzzy matching: if the exact Slug match fails, try a case-insensitive substring match against the Slug and Name of every row. One match: use it. Multiple: present options. Zero: report, list the available slugs, and exit.

Resolve the idea once, against one read of the Ideas database, and keep the row's URL for the rest of the run. That one read also serves as the portfolio index in Step 1.

## Reference Material

`incubator-reference.md` is a thin section index. Load only the `reference/` section files this skill needs:

- `reference/stage-model.md` — seed-stage semantics
- `reference/frontmatter-schema.md` — Domain, Themes, Related ideas fields
- `reference/templates.md` — Seed Template (validation) and TL;DR header fields (drafting)
- `reference/architecture.md` — related-idea consolidation and merge mechanics

## Execution Flow

### Step 1: Load Context

Load in parallel:

1. **Seed row** — fetch the resolved row: its fields and full body
2. **Portfolio index** — Read the Ideas database (conventions, Reading a database): every row that is not at Stage `archived`, with its fields. Then apply tiered reading:
   - **Complete-stage ideas:** Fields only, from the database read. Extract: Stage, Themes, Domain.
   - **All other stages:** Fetch each row (in parallel) and take its body up to the first `###` heading. Extract: fields + header fields.
   From the loaded index, extract the **portfolio theme vocabulary** (all unique Themes values).
3. **Persona guide** — load the skill named by the `persona_skill` configuration key with the Skill tool. If `persona_file=<path>` was passed, Read that file instead. A persona file that only points somewhere else (a redirect to a skill or to another file, with no guidance of its own) is refused: report it and exit. (voice calibration for drafted fields)

### Step 2: Validate

Confirm:

- Stage field is `seed`
- `### Original Capture` section exists in the body and is non-empty
- Domain and at least one Themes value set on the row

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

**Voice:** Header fields follow the persona guide — confident, declarative, specific, no hedging.

### Step 4: Surface Related Ideas

Using the portfolio index from Step 1, find related ideas at **seed, developing, drafting, or refining** stages. **Exclude complete-stage ideas** from merge/keep — they are finished work. Archived ideas are not in the index at all.

**Match criteria** — an idea is "related" if:

- It shares 2+ values in the Themes field, OR
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

**Relationship write-back:** After human confirms, update the Related ideas relation on all affected rows (`update_properties`; the value is the full list of related row URLs — the ones already there plus the ones added). A seed the human has chosen to merge away is not an affected row: its relation is not written, and it is not added to another row's relation.

**Merge mechanics** (when human says merge): Follow the same protocol as the current /develop Step 3 — primary selection, field merge, body merge with dual Original Captures, secondary archived. The merge mechanics are in `reference/architecture.md`. Write the primary first: its fields, then the secondary's Original Capture appended to the end of its body with `insert_content` under the heading `### Original Capture (merged from: {secondary slug})`. Fetch the primary and confirm that section is there. Only then archive the secondary: one `update_properties` call on the secondary's row setting `Stage` `archived` and `date:Updated:start` today (with `date:Updated:is_datetime` 0), and nothing else. Its body is left as it is and the row is never trashed. From then on the secondary is out of every seed list, name resolution and portfolio index (conventions, Addressing an idea); the primary's merged-from heading is the record of where it went.

**Which seed the run continues on.** The human picks the primary, and it can be either seed. After the merge the run continues on the primary, which now holds both captures (`reference/architecture.md`, Merge Mechanics, step 5):

- **The seed being refined is the primary:** go on to Step 5 with it.
- **The seed being refined is the secondary** (the human merged it into the other seed): it is archived, and this run is finished with it. Say so: `Seed '{secondary slug}' was merged into '{primary slug}' and is archived. Continuing on '{primary slug}'.` Drop the interpretation and the header fields drafted for it in Step 3. The primary is now the seed being refined: fetch its row, validate it (Step 2), interpret it from its body as it now stands, both captures included (Step 3), surface its related ideas from the index already loaded, the archived secondary left out (Step 4), and take Steps 5 and 6 on it. If the primary fails Step 2, or the human does not want to go on, end the run with `Seed '{secondary slug}' was merged into '{primary slug}' and is archived. Refine '{primary slug}' next: /refine-seed {primary slug}.`

Either way the archived secondary gets no write after the one call that archived it: no header, no fields, no relation. It is never presented in Step 5, never written in Step 6 and never reported as refined or ready.

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

After human approval, update the idea row: the row of the seed the run is on now, which after a merge is the primary (Step 4, Which seed the run continues on). A row at Stage `archived` is never written; if the fresh fetch below shows the row is archived, stop and report `Idea '{slug}' is archived.`

Write the body first, then the fields.

**Body update:** Write the header fields above Original Capture:

```markdown
## [Idea Title]

**Core insight:** {approved}
**Source:** {approved}
**Initial strategic connection:** {approved}

### Original Capture
{preserved verbatim}
```

Work from a fresh fetch of the row and change only the blocks above the `### Original Capture` heading, with one `update_content` call holding one operation per block:

- the `##` title heading → the `##` title heading (leave the operation out if the title is unchanged)
- the first block after the title (the draft header fields, where the seed has them) → the three approved header lines, written as one paragraph with a single line break between lines (Notion returns them joined by `<br />`)
- any further block above `### Original Capture` → an empty `new_str`, which removes it

If the body has nothing above `### Original Capture`, put the title heading and header paragraph in with `insert_content` at position `start`. If it has only the title heading above `### Original Capture`, which is what a fresh seed from the template has, replace that heading with the heading followed by the header paragraph in one operation.

Never put the `### Original Capture` heading or anything below it in an `old_str` or a `new_str`: text that is never sent cannot be altered. That is how the capture is preserved verbatim.

**Field updates** (one `notion-update-page` `update_properties` call):

- `date:Updated:start`: today's date
- `Themes` — updated per theme check. Every value must be an existing option of the Themes field; a theme that is not an option is not written — tell the human it has to be added to the field first.
- `Related ideas` — updated per Step 4
- Any other field adjustments agreed with human (within each field's options)

Report: "Seed refined: {idea-name}. Ready for /develop." `{idea-name}` is the slug of the row just written. After a merge that is the primary, and the report adds: "Merged in and archived: {secondary slug}."

## Stop Rules

| Condition | Action |
| ----------- | -------- |
| No Original Capture | Cannot refine — nothing to interpret. Exit. |
| Idea not at seed stage | Report current stage. Exit. |
| Seed is a clear duplicate of an existing idea | Present the duplicate, recommend merge (which archives the secondary) or keeping both. Wait for human. |
| The human merges the seed being refined into another seed | It is archived. Stop refining it and say so; continue on the primary, or end naming the primary as the seed to refine next (Step 4). Never write to it again or report it ready. |
| Core insight too vague to draft after reading capture | Ask the human: "What's the one-sentence version of this idea?" Use their answer. |

## Error Handling

| Condition | Behavior |
| ----------- | ---------- |
| No argument and no seed-stage ideas | Report and exit |
| Idea row not found | Fuzzy match, report available slugs, exit |
| Idea not at seed stage | Report current stage, exit |
| Row cannot be read, or a field holds a value this skill does not recognise | Report specific issue, exit |
| Related idea row cannot be read | Log, continue with valid rows |
| Persona guide not found (`persona_skill` does not load, or `persona_file` is missing or only a pointer) | Report: missing persona guide, exit |
| A Notion call fails or the connector is not reachable | Report the call and the error, exit — do not fall back to local files |

## Scope Boundaries

This skill does NOT:

- Conduct research (that's /develop's job)
- Assess impact dimensions (that's the synthesis agent's job)
- Draft output documents (that's /draft's job)
- Classify or route inbox items (that's the router's job)
- Develop the seed beyond header fields (Core insight, Source, Strategic connection + related ideas)
- Change the seed's stage (it stays at `seed` — /develop changes it to `developing`). The one Stage write it makes is `archived` on the secondary of a merge the human approved.
- Make merge decisions autonomously (always presents to human)
