---
name: develop-synthesis
description: Strategic synthesis step for /develop — transforms a seed + research handoff into a TL;DR card. Invoked by the /develop orchestrator after research is complete, or directly for testing. Takes an idea name or the idea row's URL; reads the seed row and research handoff from Notion, applies strategic reasoning to produce the card.
argument-hint: "[idea-name | idea-row-url] [notion_ideas=...] [notion_research=...] [notion_config=...] [handoff=...] [persona_file=...]"
context: fork
agent: develop-synthesis
disable-model-invocation: false
allowed-tools:
  - Read
  - Skill
  - Bash(date:*)
  - mcp__notion__notion-fetch
  - mcp__notion__notion-query-data-sources
  - mcp__notion__notion-update-page
---

# /develop-synthesis — Strategic Synthesis Step

Transforms a seed-stage idea and its research handoff into a completed TL;DR card. This is the judgment-heavy step of the /develop pipeline — the agent carries the strategic reasoning framework.

Normally invoked by the /develop orchestrator after research (Steps 0-4) is complete. Can also be invoked directly for testing or re-synthesis.

## Where Things Are

Ideas, research and configuration live in Notion. The shared mechanics — the pointers and their overrides, addressing an idea, finding research rows, writing to a card, how Notion returns text, configuration, the persona — are stated once in `reference/skill-conventions-notion-access.md`. Read it before Step 0. This skill uses three pointers from the instruction file (`CLAUDE.md`, front matter): `notion_ideas`, `notion_research` and `notion_config`.

## Arguments

Parse `$ARGUMENTS`: the first token that is not `key=value` names the idea; every `key=value` token is an override.

| Input | Behavior |
| ------- | ---------- |
| Empty | Report error: idea name required. Exit. |
| A Notion row URL | The idea row, as `/develop` and other skills pass it. Fetch it and use it. |
| `idea-name` | Resolve to the Ideas row whose Slug is `idea-name` |
| `idea-name.md` | Strip `.md`, resolve as above |

If the exact match fails, try a case-insensitive substring match against the Slug and Name of every row. One match: use it. Multiple: list and exit. Zero: report and exit.

| Override | Effect |
| ---------- | -------- |
| `notion_ideas=<database URL>` | Use this Ideas database instead of the pointer |
| `notion_research=<database URL>` | Use this Research database instead of the pointer |
| `notion_config=<page URL>` | Use this Configuration page instead of the pointer |
| `handoff=<Notion row URL or file path>` | Read the research handoff from here instead of looking for a handoff row. `/develop` passes the handoff row it wrote. |
| `persona_file=<file path>` | Read the persona guide from this file instead of loading the `persona_skill` |

A file path given to `handoff=` or `persona_file=` is absolute, or relative to the directory the session runs in.

## Execution

### Step 0: Parse Arguments

1. Read `$ARGUMENTS`
2. If no idea is named: report "Error: idea name required." and exit.
3. Settle the three pointers: an override where one is given, the `CLAUDE.md` front matter otherwise.
4. Resolve the idea to a row:
   - If the idea argument is a Notion row URL, fetch it. If the database it is in is not `notion_ideas`, report and exit.
   - Otherwise read the Ideas view and match the argument, with any `.md` stripped, against the Slug field exactly
   - If not found, try a case-insensitive substring match against the Slug and Name of all rows
   - If exactly one match, use it
   - If multiple matches, list and exit
   - If zero matches, report the available slugs and exit

### Step 1: Load Context

Fetch the idea row first (unless Step 0 already did): one fetch returns its fields and its body (the card). Then load the rest, in parallel where one does not depend on another (the related ideas wait on the handoff):

1. **Seed** — the idea row's fields and full body
2. **Research handoff** — one of:
   - `handoff=` was passed: a Notion row URL is fetched, and its body is the handoff; a file path is read with Read.
   - Otherwise, find it by type, never by a folder or file name: the idea's Research rows whose Research type is `synthesis-handoff` (conventions, Finding them). With one row, fetch it: its body is the handoff. With several, take the newest by the conventions' rule; if the rule cannot order two of them, list them and exit.
   - If not found: report "No research handoff found for {idea-name} — run /develop research phase first or create manually for testing." Exit.
3. **Configuration** — fetch the `notion_config` page and read `persona_skill` and `example_card` from its `yaml` block
4. **Persona guide** — if `persona_file=` was passed, Read that file; if its content is only a pointer elsewhere, refuse it with the conventions' message and exit. Otherwise load the skill named by `persona_skill` with the Skill tool.
5. **Format example** — fetch the page `example_card` names
6. **Related ideas** — If the handoff includes a Portfolio Context section, use that and fetch nothing. Otherwise read the idea row's Related ideas relation: for each related row, fetch it and take its fields and its body up to the first `###` heading — enough to get the header fields (Core insight, Problem, Who cares, Strategic connection). If the relation is empty and the handoff has no Portfolio Context, there are no related ideas: go on without them.

### Step 2: Validate

Confirm:

- The idea row exists and its Stage field is `seed`
- Research handoff exists and is non-empty
- Persona guide loads successfully

If the row is not at Stage `seed`: report current stage and exit. The orchestrator is responsible for validating stage before invocation; this is a safety check.

### Step 3: Synthesize

Apply the reasoning dimensions from the agent definition (The User's Moment, The Single Strategic Move, The Compound, The Strategic Connection, The Unique Territory) to produce the TL;DR card content. The agent definition carries the full reasoning framework, rubrics, voice requirements, and output template.

Write the completed card to the idea row. Write the body first and the fields second, as two calls: a run that stops between them leaves a card that still reads as a seed in its fields, which is the safe way round.

- Replace body content above `### Original Capture` with the TL;DR template
- Preserve `### Original Capture`
- Update fields (Stage, Updated, impact dimensions)

**Body.** Work from the body as the Step 1 fetch returned it; fetch again if anything has written to the row since. The blocks above the `### Original Capture` heading are the seed's `##` title heading and its header paragraph. Replace them with one `notion-update-page` `update_content` call whose `content_updates` hold one operation per block, each `old_str` being that one block's text exactly as fetched (`<b>`, `<br />` and escapes included):

- the `##` title heading → the card's `##` title heading. If the card's title line is the same as the seed's, leave this operation out: an operation that changes nothing is not sent.
- the header paragraph → everything else in the card, from the `**Core insight:**` line through the last Open Questions bullet
- any further block above `### Original Capture` → an empty `new_str`, which removes it

Never put the `### Original Capture` heading or anything below it in an `old_str` or a `new_str`: text that is never sent cannot be altered.

Write the card in Markdown, in this form:

- **The four header fields are one paragraph.** Four lines in the order Core insight, Problem it addresses, Who cares, Strategic connection, each beginning with its bold label (`**Core insight:**`), joined by `<br>` and nothing else: `**Core insight:** …<br>**Problem it addresses:** …<br>**Who cares:** …<br>**Strategic connection:** …`. No blank line between them, no list, no table.
- A blank line after each heading.
- The Opportunity Assessment as a pipe table.

If an operation matched nothing — a warning when other operations matched, a failed call when none did — fetch the row again and repeat that operation with text from the fresh fetch.

**Fields.** After the body call has succeeded, one `notion-update-page` `update_properties` call:

| Field | Value |
| ------- | ------- |
| `Stage` | `developing` |
| `date:Updated:start` | today's date, `YYYY-MM-DD`, the local date from `date +%Y-%m-%d` (with `date:Updated:is_datetime` 0) |
| `Customer sentiment`, `User experience`, `Revenue potential`, `Industry disruption`, `Strategic alignment` | `none`, `low`, `medium` or `high` |

A dimension the card marks "Insufficient data" has no field value: leave that field out of the call and keep the wording in the card's table. Never write a value outside a field's options. Set no other field.

### Step 4: Report

Present what was produced:

```text
Synthesis complete: {idea-name}

Impact dimensions: {CS}/{UX}/{RP}/{ID}/{SA}
Card written to: {URL of the idea row}
```

## Error Handling

| Condition | Behavior |
| ----------- | ---------- |
| No argument provided | Report: idea name required. Exit. |
| Idea row not found | Fuzzy match, report available slugs. Exit. |
| Research handoff not found | Report: run research phase first. Exit. |
| Seed not at seed stage | Report current stage. Exit. |
| Persona guide not found | Report: missing persona guide. Exit. |
| `persona_file=` holds only a pointer elsewhere | Refuse it with the conventions' message. Exit. |
