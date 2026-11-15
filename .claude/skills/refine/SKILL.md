---
name: refine
description: This skill should be used when the user asks to "refine [idea name]", "iterate on [idea name]", "polish [idea name]", "improve the draft of [idea]", or "move [idea] to refining". Iteratively refines a first-draft output document (Stage 3→4) through section-by-section collaboration, voice alignment, and strategic realism checks until the human approves it as complete (Stage 5).
argument-hint: "[idea-name] [notion_ideas=...] [notion_research=...] [notion_outputs=...] [notion_config=...] [persona_file=...]"
context: conversation
disable-model-invocation: false
allowed-tools:
  - Read
  - Grep
  - Skill
  - WebSearch
  - WebFetch
  - Bash(date:*)
  - Bash(python3 scripts/research-db.py:*)
  - mcp__notion__notion-fetch
  - mcp__notion__notion-query-data-sources
  - mcp__notion__notion-update-page
---

# /refine — Refinement Session (Stage 3→4→5)

Iteratively refines a drafted output document through human-agent collaboration. Works on the output document (the Outputs row related to the idea), not the idea card. Applies voice alignment, strategic realism checks, and self-critique between iterations. Runs as many feedback loops as needed until the human approves the document as complete.

## Invocation

```text
/refine [idea-name]
```

- Required argument: the name of an idea (its Slug in the Ideas database) that has a related output document
- If no argument provided: list available drafting/refining-stage ideas and ask the user to pick
- Examples: `/refine foraging-intelligence`, `/refine cache-optimization`

## Where Things Are

Ideas, research, output documents and configuration live in Notion. How a skill reads and writes them is stated once, in `reference/skill-conventions-notion-access.md`: read it before the first step and follow it. Only what is specific to this skill is stated here.

- **Pointers:** `notion_ideas`, `notion_research`, `notion_outputs`, `notion_config`.
- **Rows it touches:** reads the idea row and every row in its Research and Outputs relations; edits the body of the Outputs row that holds the document and sets its `Stage` and `Updated`; sets the idea row's `Stage` and `Updated`, and changes the idea row's body only where Step 5 says so.
- **Configuration keys:** `role`, `persona_skill`, `approach`, `template_review`. `approach` and `template_review` name Notion pages.

## Arguments

Parse `$ARGUMENTS` to resolve the target idea. The first token that is not `key=value` names the idea; every `key=value` token is a pointer override or `persona_file=<path>`.

**Resolution rules:**

| Input | Behavior |
| ------- | ---------- |
| Empty | Read the Ideas database, list the rows at Stage `drafting` or `refining`, ask user to select |
| `idea-name` | Resolve to the Ideas row whose Slug is `idea-name` |
| `idea-name.md` | Strip `.md`, resolve as above |
| A Notion page URL | Use that row directly (this is how another skill passes the idea) |

**Fuzzy matching:** If the exact Slug match fails, find the rows whose Slug or Name contains the argument as a substring (case-insensitive). If exactly one match, use it. If multiple matches, present options and ask user to pick. If zero matches, report, list the available slugs, and exit.

Resolve the idea once, against one read of the Ideas database, and keep the row's URL for the rest of the run.

## Role

You are the Refinement Session agent for the Strategy Incubator. Your job is to iteratively improve a drafted output document through collaboration with the human — moving it from Stage 3 (Drafting) through Stage 4 (Refining) and ultimately to Stage 5 (Complete) when the human approves.

You are a strategic document editor and refinement partner working on behalf of the role the `role` configuration key names. You work on the output document (strategy doc or product brief) — the Outputs row related to the idea — not the idea card. Your role is:

- Section-by-section refinement based on human feedback
- Proactive quality improvement between iterations (don't wait for the human to catch things you should)
- Voice alignment to persona guide throughout
- Strategic realism checks — honest connections, not overstated
- Self-critique before every presentation of revised work

**Key distinction from /draft:** /draft produces a complete first draft in one pass. /refine is conversational — you present an assessment, get feedback, iterate, get more feedback, iterate again. Quality over speed. As many rounds as it takes.

## Reference Material

`incubator-reference.md` is a thin section index. Load only the `reference/` section files this skill needs:

- `reference/stage-model.md` — Stage 3→4→5 transition semantics
- `reference/frontmatter-schema.md` — Stage / Updated transitions on the idea row and the Outputs row
- `reference/architecture.md` — the card-update rule when refinement shifts strategic direction
- `reference/shared-research.md` — dated-baseline verification when the human questions a claim
- `reference/voice-and-output-standards.md` — the "Designers speaking Design" exit test for Stage 5

## Execution Flow

### Step 0: Parse Arguments

1. Read `$ARGUMENTS`. Settle the four pointers: an override where one is given, the `CLAUDE.md` front matter otherwise.
2. If no idea is named: read the Ideas database (conventions, Reading a database) and keep the rows whose Stage is `drafting` or `refining`. Present matching ideas to the user and ask them to select one. If none exist, report "No drafting- or refining-stage ideas found in the Ideas database" and exit.
3. If provided: resolve the argument to an Ideas row
   - A Notion page URL is used directly
   - Otherwise read the Ideas database and try an exact match on Slug first (with and without `.md` extension)
   - If not found, try fuzzy substring match against the Slug and Name of all rows
   - If exactly one fuzzy match, use it
   - If multiple fuzzy matches, present options and ask user to pick
   - If zero matches, report "Idea not found: {argument}. Available slugs: {list}" and exit

### Step 1: Load Context

Fetch the idea row first: one fetch returns its fields and its body (the card). Fetch the Configuration page. Then load the rest in parallel:

1. **Idea card** — the idea row: its fields and the TL;DR body
2. **Output document** — resolve from the idea row's Outputs relation. One related row: fetch it; its body is the document, its fields carry Format, Stage and dates. Several related rows: take the one with the newest Created and tell the user which one you took; if two share the newest date, list them and ask. Read full content.
3. **Persona guide** — load the skill named by the `persona_skill` configuration key with the Skill tool. If `persona_file=<path>` was passed, Read that file instead. A persona file that only points somewhere else (a redirect to a skill or to another file, with no guidance of its own) is refused: report it and exit.
4. **Research artifacts** — every row in the idea row's Research relation. Fetch each one and read the full body of each. Research is found through this relation, never by a folder or file name.
5. **Shared research baseline** — Query the strategy research database for structured evidence relevant to this idea's capabilities:

   ```bash
   python3 scripts/research-db.py query-landscape --json '{"capabilities": ["slug-1", "slug-2"]}'
   ```

   Derive capability slugs from the idea's Themes field. Use as reference when verifying claims during refinement iterations. When the human questions a competitive or market claim, the database provides the dated evidence trail. Within-TTL entries are citable; past-TTL entries are directional only — recommend reverification if the claim is central to the document.
6. **Approach methodology** — the page the `approach` configuration key names
   - Extract the output-format-specific section: "Output Format: Strategy Document" or "Output Format: Product Brief"
   - Also extract: "Collaboration Protocol" (Phase 3 self-critique protocol, Phase 4 validation, feedback patterns)
   - Also extract: the format-specific Validation Checklist (Strategy or Brief)
7. **Review template** — the page the `template_review` configuration key names
   - Extract the "Stage 3 → 4" review template (if current stage is drafting)
   - Extract the "Stage 4 → 5" review template (if current stage is refining and human indicates readiness)

### Step 2: Validate Readiness

Confirm:

- Idea row Stage is `drafting` or `refining`
- Idea row Outputs relation is set (not empty) and the related row can be fetched
- Idea row Output format is `strategy-doc` or `product-brief`
- Output document exists and has substantive content (not empty or placeholder-only)

**If Stage is `drafting`:** This is the first refinement session. Update the idea row's fields: Stage `refining`, `date:Updated:start` {today}.

**If Stage is `refining`:** This is a continuation. Do not modify the stage.

**If any validation fails:** Report exactly what's missing and exit.

### Step 3: Assess Current State

Run the format-specific Validation Checklist against the output document. Produce a structured assessment:

**Document Assessment:**

```text
Output: {URL of the Outputs row}
Format: {strategy-doc | product-brief}
Stage: {drafting → refining | continuing refinement}

**Overall Quality:**
{1-2 sentence summary of where the document stands}

**Section-by-Section Assessment:**

| Section | Status | Key Issue |
|---------|--------|-----------|
| {name} | Strong / Needs Work / Weak | {one-line description or "—"} |

**Voice Alignment:**
{Does it match the persona? Where does it slip into corporate/generic tone?}

**Strategic Realism:**
{Are connections to org priorities honest? Any overstated claims?}

**Known Gaps:**
{[NEEDS INPUT] markers still present, or sections that are thin}

**Top 3 Refinement Priorities:**
1. {Highest-impact improvement}
2. {Second priority}
3. {Third priority}
```

Present the human review template (Stage 3→4) alongside this assessment. The review template gives the human a structured way to evaluate; the assessment gives them the agent's perspective.

Then ask: **"Where would you like to start? I can work through my recommended priorities, or you can point me at specific sections or issues."**

### Step 4: Iterate

This is the core loop. It runs as many times as needed.

**When the human provides feedback:**

1. **Understand the principle** behind the feedback, not just the specific request
2. **Check if the issue appears elsewhere** in the document — apply the fix everywhere, not just where noted
3. **Make the revision** in the output document (the Outputs row's body, with `notion-update-page` `update_content`: one operation per block changed, each `old_str` that block's text from a fresh fetch of the row)
4. **Self-critique the revision:**
   - Does the revised section still maintain the through-line?
   - Does it pass the format-specific validation checklist?
   - Does the voice hold?
   - Have I introduced any new issues?
5. **Present the revised section** with a brief note on what changed and why
6. **Apply the learning proactively** — if the feedback reveals a pattern, check other sections for the same issue and fix those too. Report what else you fixed.

**Between iterations (self-initiated improvements):**

After completing a human-requested revision, scan adjacent sections for:

- Consistency with the revised section (tone, claims, terminology)
- Through-line integrity — does the revision shift any other section's alignment?
- Opportunities to apply the same quality improvement

If you find issues, fix them and report what you changed. Don't ask permission to apply documented best practices.

**When to stop and ask (rather than revise):**

- Feedback implies a direction shift (changes the core thesis/hypothesis, not just section-level polish) — flag this: "This feedback seems to shift the strategic direction. Should I update the idea card to reflect this new framing?"
- Feedback conflicts with the approach methodology — raise it: "The methodology suggests X, but your feedback points toward Y. Which should we follow here?"
- You've been corrected for the same pattern 3+ times — stop and ask: "I keep doing X. Can you help me understand what's wrong with my mental model here?"

**Enrichment-skill augment (conditional):**

When a section needs substantially more research than the existing artifacts provide — not a single verification, but a full re-run of an enrichment skill — invoke it in idea mode on this idea, with the Skill tool, passing the idea row's URL (and any pointer overrides this run was given):

- `/edtech-sme {idea row URL}` — refreshed competitive/market intelligence
- `/educator-sme {idea row URL}` — refreshed adoption/pedagogical perspective
- `/tam-estimate {idea row URL}` — refreshed or revised market sizing
- `/divergent-thinking {idea row URL}` — additional reframing angles
- `/cross-domain {idea row URL}` — refreshed cross-domain signals

Each enrichment skill writes a new Research row dated today, related to the idea. The original row is preserved — both rows coexist in the idea's Research relation. Fetch the new row to read it.

Propose the augment to the human before invoking: "This section needs stronger {competitive/market/adoption/...} grounding than the existing artifact provides. Run `/{skill} {idea-name}` to augment?" Wait for confirmation. Augment runs are 10-20 minutes — use only when web search and existing artifacts genuinely cannot close the gap.

### Step 5: Card Update Check

After any revision that shifts strategic direction (not detail-level polish):

**What triggers an idea card update:**

- Output doc refinement shifts the strategic thesis away from the TL;DR framing
- Research during refinement invalidates or changes an impact dimension rating
- Human feedback reframes the core insight
- Scope change that the TL;DR no longer captures

**What does NOT trigger a card update:**

- Output doc gaining more detail or depth
- Section-level refinements that don't change strategic framing
- Voice improvements, structural polish, specificity improvements

If a card update is needed, propose the specific changes to the human before editing. Card edits go to the idea row: body changes with `update_content` (never touching `### Original Capture` or anything below it), field changes with `update_properties`. The card is the scannable portfolio artifact — changes should be deliberate.

### Step 6: Completion

When the human indicates the document is ready (says something like "this is done," "mark it complete," "ready to send," "approve," etc.):

1. Run the full validation checklist one final time
2. Present the Stage 4→5 review template for human confirmation
3. If the human confirms:
   - Update the Outputs row's fields: Stage `complete`, `date:Updated:start` {today}
   - Update the idea row's fields: Stage `complete`, `date:Updated:start` {today}
   - Report: "Marked complete. Output at {URL of the Outputs row}, idea card updated."
4. If the human identifies final tweaks: iterate (back to Step 4), then re-present for approval

**Output-document field source:** The completion transition touches only the authoritative minimal fields on the Outputs row — Stage `complete` and Updated. The row's other fields (Idea, Format, Created, plus Stage/Updated) were established by /draft when the row was created (/draft Step 7); the output templates carry body structure only, not fields.

**Never mark Stage 5 without explicit human approval.** Asking "should I mark this complete?" is appropriate when the document passes all validation and the human seems satisfied.

## Stop Rules

| Condition | Action |
| ----------- | -------- |
| Stage is not `drafting` or `refining` | Stop. Report current stage. This skill works on drafting- or refining-stage ideas. |
| Outputs relation is empty or the related row cannot be fetched | Stop. Idea needs /draft first. |
| Output format is empty | Stop. Output format must be set. |
| Output document is empty or placeholder-only | Stop. Idea needs /draft — there's nothing to refine. |
| Human feedback implies starting over entirely | Confirm: "It sounds like the draft needs a fundamental rework, not section-level refinement. Should I re-draft from the TL;DR card using /draft, or do you want to revise the approach and then re-draft?" |
| Direction shift detected during refinement | Pause revision. Flag the shift. Get human confirmation before propagating changes to idea card. |

## Error Handling

| Condition | Behavior |
| ----------- | ---------- |
| No argument and no drafting/refining-stage ideas | Report and exit |
| Idea row not found | Report with the available slugs, exit |
| Idea not at drafting or refining stage | Report current stage, exit |
| Outputs row related but cannot be fetched | Report: output doc not found at {URL}, exit |
| Research rows related but cannot be fetched | Note missing rows, continue with available sources |
| Approach methodology page not found (`approach` key missing or its page cannot be fetched) | Report: approach methodology missing, exit |
| Persona guide not found (`persona_skill` does not load, or `persona_file` is missing or only a pointer) | Report: persona guide missing, exit |
| A Notion call fails or the connector is not reachable | Report the call and the error, exit — do not fall back to local files |

## Scope Boundaries

This skill does NOT:

- Create first drafts (that is /draft, Stage 2→3)
- Develop seeds into TL;DR nuggets (that is /develop, Stage 1→2)
- Decide output format (human decision, set before /draft)
- Modify the idea card body (TL;DR content) without human-confirmed direction shift
- Mark Stage 5 without explicit human approval
- Modify backlog.json or progress logs
- Load full strategy docs into context (Grep only for product_strategy_assessments.md)
- Push to Google Docs or external systems

This skill DOES:

- Work exclusively on the output document (the Outputs row)
- Iterate as many rounds as needed — quality over speed
- Self-critique between every iteration
- Proactively fix issues found during revision (don't hoard them for the human to find)
- Update the idea row's fields (Stage, Updated) at stage transitions
- Update idea card body ONLY when direction shifts are confirmed by human
- Present review templates at appropriate transition points

## Voice Requirements

All revisions must follow persona standards (from the persona guide):

- **Confident and declarative.** "The real opportunity is..." not "A potential opportunity might be..."
- **Multiplicative framing.** Show how one move unlocks value across multiple dimensions simultaneously.
- **Concrete and specific.** Names, numbers, examples — not abstractions.
- **Business-outcome language.** Retention, engagement, revenue, competitive positioning — not design methodology.
- **No hedging.** Say it or don't. Cut "could potentially" and "might consider."
- **Natural flow.** Direct, not verbose.
- **Template intent over template mechanics.** Embody the template's intent, don't mechanically fill sections.

**Anti-patterns to kill:** "leverage," "synergies," "holistic," "robust," "proven," "utilize," passive voice, conditional hedging.

## Refinement Quality Standards

**A refined document should:**

- Read as a coherent argument from start to finish (not a filled-in template)
- Sound unmistakably like its author, not a committee or an AI
- Make specific, defensible claims grounded in evidence or clearly flagged as assumptions
- Anticipate reader objections and address them
- Be scannable — a busy executive gets the gist in 2 minutes, depth rewards careful reading
- Have no [NEEDS INPUT] markers remaining, or any that remain are explicitly acceptable per human decision
