---
name: revert-to-seed
description: Reverts a developing-stage idea card to seed stage for re-development. Preserves identity fields and Original Capture, moves the idea's research rows to the trash and clears synthesis content, and runs /refine-seed with the developed header fields as autonomous confirmation of direction. Temporary remediation skill for cards developed without enrichment agents.
argument-hint: "[idea-name] [notion_ideas=...] [notion_config=...] [persona_file=...]"
context: conversation
disable-model-invocation: false
allowed-tools:
  - Read
  - Bash(date:*)
  - Skill
  - mcp__notion__notion-fetch
  - mcp__notion__notion-query-data-sources
  - mcp__notion__notion-update-page
---

# /revert-to-seed — Revert Developed Card to Seed Stage

Reverts a developing-stage idea card to seed stage so it can be re-developed with the full enrichment-integrated /develop pipeline. Clears research artifacts and synthesis content while preserving the idea's identity. Then runs /refine-seed using the developed card's header fields as autonomous direction confirmation.

**This is a temporary remediation skill** for cards developed before enrichment agents were integrated into /develop. Once all cards are remediated, this skill can be archived.

## Invocation

```text
/revert-to-seed [idea-name]
```

- Required argument: the name of a developing-stage idea (its Slug in the Ideas database)
- Only operates on ideas at Stage `developing`

## Where Things Are

Ideas, research, output documents and configuration live in Notion. How a skill reads and writes them is stated once, in `reference/skill-conventions-notion-access.md`: read it before the first step and follow it. Only what is specific to this skill is stated here.

- **Pointers:** `notion_ideas`, `notion_config`. Both, and any `persona_file=`, are passed on to `/refine-seed` in Step 4.
- **Rows it touches:** reads the idea row and every row in its Research relation; moves the idea's own Research rows to the trash and empties the idea's Research relation; unlinks a shared Research row from this idea; rewrites the idea row's body above `### Original Capture` and resets its fields.
- **The trash:** this is the one skill that calls `mcp__notion__notion-delete-pages`. What that tool does, its `user_confirmed` argument, its limit of 20 rows a call, the 30 days a trashed row can be restored, and why the tool is in no `allowed-tools` list are in the conventions (Calls, The trash; Tool lists).

## Arguments

Parse `$ARGUMENTS` to resolve the target idea. The first token that is not `key=value` names the idea; every `key=value` token is a pointer override or `persona_file=<path>`, passed on to /refine-seed in Step 4.

| Input | Behavior |
| --- | --- |
| Empty | Read the Ideas database, list the rows at Stage `developing`, ask user to select |
| `idea-name` | Resolve to the Ideas row whose Slug is `idea-name` |
| A Notion page URL | Use that row directly |

Fuzzy matching: if the exact Slug match fails, try a case-insensitive substring match against the Slug and Name of every row. One match: use it. Multiple: present options. Zero: report, list the available slugs, and exit.

Resolve the idea once and keep the row's URL for the rest of the run.

## Reference Material

`incubator-reference.md` is a thin section index. Load only the `reference/` section files this skill needs:

- `reference/stage-model.md` — developing→seed reversion semantics
- `reference/frontmatter-schema.md` — which identity fields to preserve vs. clear
- `reference/templates.md` — Seed Template (the state the card is rewritten to)

## Execution Flow

### Step 1: Load and Validate

1. Fetch the developed card — the idea row: its fields and full body.
2. Verify Stage is `developing`. If not, report and exit.
3. Extract and save for later use:
   - **Header fields:** Core insight, Problem it addresses, Who cares, Strategic connection
   - **Original Capture:** The `### Original Capture` section (it stays in the body untouched; confirm it exists)
   - **Identity fields:** Related ideas, Initiative, Source, Type, Themes, Jira key, Jira pushed
4. Read the row's Research relation — these are the research rows to clean up.

### Step 2: Clean Up Research Artifacts

Move the idea's own research rows to Notion's trash. Preserve research shared with another idea.

1. Read the idea row's Research relation. Fetch each related row.
2. Only rows related to this idea are touched, and a row is this idea's own only if its Idea relation holds this idea and no other. A row whose Idea relation also holds another idea is shared: it is never trashed.
3. Move the idea's own research rows to the trash (the handoff, development research, cross-domain signals, and any enrichment artifacts from prior runs — every own row, whatever its Research type). This is destructive: list the rows to the human (Name, Research type, URL), say that they go to Notion's trash and can be restored from it for 30 days, get their explicit confirmation, then call `mcp__notion__notion-delete-pages` with those rows' page IDs and `user_confirmed: true`, as the conventions describe it (Calls, The trash: at most 20 IDs a call; the tool is in no `allowed-tools` list). Never set `user_confirmed: true` before the human has confirmed this exact list. If confirmation is declined or not given, stop: leave the research rows and the idea's Research relation exactly as they are, report that the revert did not run, and do not continue to Step 3.
4. Shared research rows are NOT trashed — they are durable contributions another idea still uses. Unlink each from this idea only: set the shared row's Idea relation to its other ideas, leaving this one out.

After the trash calls, fetch the idea row again. A trashed row stays listed in the idea's Research relation, so empty the relation yourself (the counterpart of `research: []`): write it as the same list without the trashed rows (`update_properties`; `[]` when every row was trashed), and say in Step 5 that a row restored from the trash will then need relating to the idea again.

### Step 3: Revert the Card

Write the idea row back to seed state.

Write the body first, then the fields: a run that stops in between leaves a row whose Stage still says `developing`.

**Body — seed template with Original Capture:**

```markdown
## {Title from developed card}

**Core insight:** {from developed card header fields}
**Source:** {the row's Source field — or "Reverted from developed card" if it is empty}
**Initial strategic connection:** {Strategic connection from developed card}

### Original Capture
{preserved verbatim from developed card}
```

Work from a fresh fetch of the row and change only the blocks above the `### Original Capture` heading, with one `update_content` call holding one operation per block (at most 100 operations a call; use a second call for more):

- the `##` title heading → left as it is (no operation: the title does not change)
- the first block after the title (the header fields: Core insight, Problem it addresses, Who cares, Strategic connection — one paragraph, or the first of several) → the three seed header lines, written as one paragraph with a single line break between lines
- every further block above `### Original Capture` (the Opportunity Assessment table, Research Summary, Thought Outline, Open Questions and the rest of the developed card) → an empty `new_str`, which removes it

Never put the `### Original Capture` heading or anything below it in an `old_str` or a `new_str`: text that is never sent cannot be altered. That is how the capture is preserved verbatim.

Fetch the row again and confirm that only the title heading and the header paragraph remain above `### Original Capture`. Repeat the removal for any block still there, with its text from this fresh fetch. If a block still remains after that, stop and report it — do not replace the whole body.

**Fields — preserve identity, clear development artifacts.** Only once the body check above has passed. One `notion-update-page` `update_properties` call that sets only these (a cleared field is set to `null`):

| Field | Value |
| ------- | ------- |
| `Stage` | `seed` |
| `date:Updated:start` | today's date (with `date:Updated:is_datetime` 0) |
| `Output format` | cleared |
| `Customer sentiment`, `User experience`, `Revenue potential`, `Industry disruption`, `Strategic alignment` | cleared |
| `Output file` | cleared |
| `Outputs` | empty (`[]`) — the counterpart of `output-file: null`. A developing idea normally has none; an Outputs row that was related is unlinked, not trashed. |
| `Blocked by` | cleared |

Every other field is preserved by not being written: Type, Created, Domain, Themes, Related ideas, Initiative, Source, Jira key, Jira pushed, and the rest. The Research relation is emptied by Step 2, not here.

Note: The header fields here come from the DEVELOPED card, not from re-interpreting the Original Capture. These are the synthesis agent's refined versions and serve as direction confirmation for /refine-seed in the next step.

### Step 4: Run /refine-seed Autonomously

Invoke `/refine-seed` with the Skill tool, passing the idea row's URL and any pointer overrides or `persona_file=` this run was given.

The seed now has:

- Original Capture (what /refine-seed interprets)
- Header fields from the developed card (what /refine-seed would normally present to the human for confirmation)

When /refine-seed presents its interpretation and drafted fields, compare them against the existing header fields from the developed card:

- **If aligned** (same intent, same strategic direction, wording may differ): confirm autonomously. The developed card's header fields serve as the human's "yes, that's the right direction" signal.
- **If divergent** (different intent, different strategic connection, or nature classification changed): stop and surface to the human. The re-interpretation disagrees with the original development direction — the human needs to decide.

A merge is never confirmed autonomously: if /refine-seed proposes merging this idea with another seed, stop and put it to the human. If the human merges this idea into the other seed, /refine-seed archives this idea and continues on the surviving seed; this idea is then out of the pipeline and is not reported as ready.

After /refine-seed completes, the seed it finished on is ready for `/develop`: this idea, or the surviving seed if this idea was merged away.

### Step 5: Present

```text
Revert complete: {idea-name}

**Reverted from:** developing → seed
**Research cleaned:** {list of the research rows moved to the trash — Name and URL; recoverable from Notion's trash for 30 days}
**Shared research preserved:** {note that research rows shared with another idea are not trashed — list any that were unlinked from this idea, or "none"}

**Refinement result:** {aligned — auto-confirmed | divergent — human decision needed on {specifics} | merged into {surviving slug} and archived, on the human's decision}

**Header fields (post-refinement):**
- Core insight: {current}
- Source: {current}
- Strategic connection: {current}

Ready for /develop.
```

If the idea was merged away in Step 4, the header fields shown are the surviving seed's and the last line names it: `Ready for /develop: {surviving slug}. '{idea-name}' is archived.`

## Error Handling

| Condition | Behavior |
| ----------- | ---------- |
| Card not at developing stage | Report current stage, exit |
| No Original Capture section | Report — card cannot be reverted without Original Capture. Exit. |
| Idea has no related Research rows | Skip cleanup, proceed with card revert |
| /refine-seed fails | Report error. Card is already reverted to seed — /refine-seed can be re-run manually. |
| /refine-seed interpretation diverges from developed header fields | Stop, surface the divergence to the human with both versions, wait for decision |

## Scope Boundaries

This skill does NOT:

- Trash any Research row that is not related to this idea, or that is also related to another idea
- Run /develop (that's the next step, invoked separately by the human)
- Modify other ideas' fields (Related ideas on sibling rows stay as-is)
- Trash the idea row — it reverts in place
