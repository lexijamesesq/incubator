---
name: revert-to-seed
description: Reverts a developing-stage idea card to seed stage for re-development. Preserves identity frontmatter and Original Capture, clears research and synthesis artifacts, and runs /refine-seed with the developed header fields as autonomous confirmation of direction. Temporary remediation skill for cards developed without enrichment agents.
argument-hint: [idea-name]
context: conversation
disable-model-invocation: false
allowed-tools:
  - Read
  - Edit
  - Write
  - Glob
  - Grep
  - Bash(date:*)
  - Skill
---

# /revert-to-seed — Revert Developed Card to Seed Stage

Reverts a developing-stage idea card to seed stage so it can be re-developed with the full enrichment-integrated /develop pipeline. Clears research artifacts and synthesis content while preserving the idea's identity. Then runs /refine-seed using the developed card's header fields as autonomous direction confirmation.

**This is a temporary remediation skill** for cards developed before enrichment agents were integrated into /develop. Once all cards are remediated, this skill can be archived.

## Invocation

```text
/revert-to-seed [idea-name]
```

- Required argument: the name of a developing-stage idea file in `Ideas/`
- Only operates on ideas at `stage: developing`

## Arguments

Parse `$ARGUMENTS` to resolve the target idea file.

| Input | Behavior |
| --- | --- |
| Empty | List all developing-stage ideas in Ideas/, ask user to select |
| `idea-name` | Resolve to `Ideas/{idea-name}.md` |

Fuzzy matching: if exact match fails, try substring match. One match: use it. Multiple: present options. Zero: report and exit.

## Reference Material

`incubator-reference.md` is a thin section index. Load only the `reference/` section files this skill needs:

- `reference/stage-model.md` — developing→seed reversion semantics
- `reference/frontmatter-schema.md` — which identity fields to preserve vs. clear
- `reference/templates.md` — Seed Template (the state the card is rewritten to)

## Execution Flow

### Step 1: Load and Validate

1. Read the developed card at `Ideas/{idea-name}.md` — full content.
2. Verify `stage: developing`. If not, report and exit.
3. Extract and save for later use:
   - **Header fields:** Core insight, Problem it addresses, Who cares, Strategic connection
   - **Original Capture:** The `### Original Capture` section (verbatim)
   - **Identity frontmatter:** related-ideas, initiative, source, type, themes, jira-key, jira-pushed-at
4. Read the `research:` frontmatter array — these are the artifact paths to clean up.

### Step 2: Clean Up Research Artifacts

Delete idea-specific research artifacts. Preserve shared research contributions.

1. Read the `research:` array from frontmatter.
2. For each path in the array, check if it's under `Research/{idea-name}/` (idea-specific) or `Research/shared/` (shared). Only delete idea-specific artifacts.
3. Delete the idea-specific research directory: `Research/{idea-name}/` and all its contents (synthesis-handoff.md, development-research.md, cross-domain-signals.md, and any enrichment artifacts from prior runs). Deletion is destructive: list the paths to the human, get their explicit confirmation, then remove them with `rm` through `Bash` (not pre-approved in `allowed-tools`, so the harness prompts as well).
4. Shared research files (`Research/shared/assessments/*.md`) are NOT touched — findings written there during the original development are durable contributions to the knowledge base.

### Step 3: Revert the Card

Write the idea file back to seed state:

**Frontmatter — preserve identity, clear development artifacts:**

```yaml
type: {preserved}
stage: seed
created: {preserved}
updated: {today's date}
output-format: null
domain: {preserved}
themes: {preserved}
customer-sentiment: null
user-experience: null
revenue-potential: null
industry-disruption: null
strategic-alignment: null
related-ideas: {preserved}
initiative: {preserved}
source: {preserved}
output-file: null
research: []
blocked_by: null
jira-key: {preserved}
jira-pushed-at: {preserved}
```

**Body — seed template with Original Capture:**

```markdown
## {Title from developed card}

**Core insight:** {from developed card header fields}
**Source:** {from developed card — or "Reverted from developed card" if original source not recoverable}
**Initial strategic connection:** {Strategic connection from developed card}

### Original Capture
{preserved verbatim from developed card}
```

Note: The header fields here come from the DEVELOPED card, not from re-interpreting the Original Capture. These are the synthesis agent's refined versions and serve as direction confirmation for /refine-seed in the next step.

### Step 4: Run /refine-seed Autonomously

Invoke `/refine-seed {idea-name}`.

The seed now has:

- Original Capture (what /refine-seed interprets)
- Header fields from the developed card (what /refine-seed would normally present to the human for confirmation)

When /refine-seed presents its interpretation and drafted fields, compare them against the existing header fields from the developed card:

- **If aligned** (same intent, same strategic direction, wording may differ): confirm autonomously. The developed card's header fields serve as the human's "yes, that's the right direction" signal.
- **If divergent** (different intent, different strategic connection, or nature classification changed): stop and surface to the human. The re-interpretation disagrees with the original development direction — the human needs to decide.

After /refine-seed completes, the seed is ready for `/develop`.

### Step 5: Present

```text
Revert complete: {idea-name}

**Reverted from:** developing → seed
**Research cleaned:** {list of deleted artifact paths}
**Shared research preserved:** {note that shared research contributions are untouched}

**Refinement result:** {aligned — auto-confirmed | divergent — human decision needed on {specifics}}

**Header fields (post-refinement):**
- Core insight: {current}
- Source: {current}
- Strategic connection: {current}

Ready for /develop.
```

## Error Handling

| Condition | Behavior |
| ----------- | ---------- |
| Card not at developing stage | Report current stage, exit |
| No Original Capture section | Report — card cannot be reverted without Original Capture. Exit. |
| Research directory doesn't exist | Skip cleanup, proceed with card revert |
| /refine-seed fails | Report error. Card is already reverted to seed — /refine-seed can be re-run manually. |
| /refine-seed interpretation diverges from developed header fields | Stop, surface the divergence to the human with both versions, wait for decision |

## Scope Boundaries

This skill does NOT:

- Touch shared research files (`Research/shared/assessments/*.md`)
- Run /develop (that's the next step, invoked separately by the human)
- Modify other ideas' frontmatter (related-ideas on sibling cards stay as-is)
- Delete the idea file — it reverts in place
