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

Ideas, research, output documents and configuration live in Notion. The repo's instruction file (`CLAUDE.md`, front matter) points to them. If the front matter is not already in context, Read `CLAUDE.md` at the repo root. The shared mechanics — pointers and overrides, addressing an idea, artifact rows, writing to a card, how Notion returns text, configuration, local documents and persona — are stated once in `reference/skill-conventions-notion-access.md`; read it before the first step. In short:

| Pointer | What it is |
| --- | --- |
| `notion_ideas` | The Ideas database. One row per idea: the card is the row's page body, the front matter is the row's fields. |
| `notion_config` | The Configuration page. Instance values, read by key name from its `yaml` block. |

A `key=value` argument named after a pointer (`notion_ideas=<database URL>`, `notion_config=<page URL>`) overrides it. That is how a test run is kept away from the live rows: it passes scratch databases with the same fields. A run with overrides reads and writes only what the overrides name.

Use only these Notion calls: `notion-fetch` (a row, page or database), `notion-query-data-sources` in view mode, and `notion-update-page`.

**Reading a database.** Fetch the database with `notion-fetch`: the result lists its data source (`collection://...`) and its views (`view://...`). Query the first view with `notion-query-data-sources` in **view mode** (never SQL or rows mode), `page_size` 100, passing `next_cursor` as `start_cursor` while `has_more` is true. Rows come back with their fields and no bodies. One `notion-fetch` of a row returns its fields and its body.

**Reading configuration.** Fetch the `notion_config` page and read values by key name from its `yaml` block. A key whose value is a Notion page URL names a page: fetch that page to read it.

**Writing.** Fields, relations included, are set with `notion-update-page` `update_properties`. A select or multi-select field takes only one of its existing options: never write a value outside them. A date is written as `date:<Field>:start` in `YYYY-MM-DD`, with `date:<Field>:is_datetime` 0. "Today" is the local date from `date +%Y-%m-%d`. One block of a body is replaced with `update_content`, one operation per block, each `old_str` that block's text copied from a fresh fetch of the row; leave out an operation whose new text equals the old. If the call warns that an operation matched nothing, fetch the row again and repeat that operation with text from the fresh fetch.

**Notion does not return text byte for byte.** `~`, `$` and `[ ]` come back escaped, a line break inside a paragraph as `<br />`, bold as `<b>`, inline code as `<code>`, a blank line is added after each heading, and a value that looks like a file name can come back wrapped as a link. The words are preserved. Wherever this skill matches or compares text (a label such as `**Core insight:**`, a heading, a field value), compare the words, never the raw string. Wherever it sends fetched text somewhere else, convert it back to Markdown first: `<b>` to `**`, `<code>` to backticks, `<br />` to a line break, escapes removed, a link added around a file name unwrapped.

**Configuration keys this skill reads:** `persona_skill`.

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
2. **Portfolio index** — Read the Ideas database (see Reading a database): every row with its fields. Then apply tiered reading:
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

Using the portfolio index from Step 1, find related ideas at **seed, developing, drafting, or refining** stages. **Exclude complete-stage ideas** from merge/keep — they are finished work.

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

**Relationship write-back:** After human confirms, update the Related ideas relation on all affected rows (`update_properties`; the value is the full list of related row URLs — the ones already there plus the ones added).

**Merge mechanics** (when human says merge): Follow the same protocol as the current /develop Step 3 — primary selection, field merge, body merge with dual Original Captures, secondary archived. The merge mechanics are in `reference/architecture.md`. In Notion there is no Archive folder and the Stage field has no `archived` option, so the secondary is not moved or restaged: leave its row as it is and tell the human it is merged into the primary and has to be archived by hand.

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

After human approval, update the idea row.

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

If the body has nothing above `### Original Capture`, put the title heading and header paragraph in with `insert_content` at position `start`.

Never put the `### Original Capture` heading or anything below it in an `old_str` or a `new_str`: text that is never sent cannot be altered. That is how the capture is preserved verbatim.

**Field updates** (one `notion-update-page` `update_properties` call):

- `date:Updated:start`: today's date
- `Themes` — updated per theme check. Every value must be an existing option of the Themes field; a theme that is not an option is not written — tell the human it has to be added to the field first.
- `Related ideas` — updated per Step 4
- Any other field adjustments agreed with human (within each field's options)

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
- Change the seed's stage (it stays at `seed` — /develop changes it to `developing`)
- Make merge decisions autonomously (always presents to human)
