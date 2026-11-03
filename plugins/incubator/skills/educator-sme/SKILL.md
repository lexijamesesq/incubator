---
name: educator-sme
description: This skill should be used when the user asks to "get educator feedback on [idea]", "educator evaluation of [idea/subject]", "teacher perspective on [idea/subject]", "classroom reality check for [idea]", or "educator SME review of [subject]". Evaluates a strategic idea OR an arbitrary subject (product, tool, methodology) through the lens of a veteran educator — 20+ years K-12 and higher ed — focused on pedagogical practice, classroom reality, and adoption likelihood.
argument-hint: [idea-name]
context: fork
agent: educator-sme
disable-model-invocation: false
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - WebSearch
  - WebFetch
  - Bash(date:*)
  - Bash(python3 scripts/research-db.py:*)
  - Bash(mkdir:*)
  - mcp__obsidian__read_note
  - mcp__obsidian__write_note
  - mcp__obsidian__update_frontmatter
---

# /educator-sme — Educator SME Evaluation

Evaluates a strategic idea through the lens of a veteran educator with 20+ years spanning K-12 and higher ed. Produces an unfiltered assessment of pain point validity, adoption realism, and classroom impact. This is an enrichment agent — it adds a research artifact without changing the idea's stage.

## Invocation

```text
/educator-sme [idea-name]                  # idea mode
/educator-sme --adhoc "subject string"     # ad-hoc mode
```

Two modes:

- **Idea mode** (naked argument): evaluates an idea file. Writes local artifact + updates idea frontmatter.
- **Ad-hoc mode** (`--adhoc "subject"`): evaluates a free-form subject (product, tool, methodology). No local artifact, no frontmatter update. DB findings still captured.

Examples: `/educator-sme foraging-intelligence`, `/educator-sme --adhoc "Top Hat"`, `/educator-sme --adhoc "standards-based grading"`.

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
| Zero matches | **ERROR**: "Idea file not found: `{arg}`. Closest candidates in Ideas/: `{list up to 5}`. For ad-hoc analysis of a non-idea subject, use: `/educator-sme --adhoc \"{arg}\"`." Exit. Do NOT silently fall through to ad-hoc. |

## Persona

This skill runs in the educator-sme agent's context. The agent carries the full veteran educator persona (20+ years K-12 and higher ed), domain calibration framework, evaluation dimensions, and quality standards. See `.claude/agents/educator-sme.md`.

**Invocation note:** When executed by a pointer-invoked agent rather than the Skill tool: generic Read/Write/Edit on vault .md files may be redirected — use the Obsidian MCP equivalents; run research-db.py from the project root.

## Execution Flow

Execute these steps in order. Stop and report errors at any step rather than continuing with bad data.

### Step 0: Parse Arguments

1. Read `$ARGUMENTS`. Detect `--adhoc` flag.
2. **If `--adhoc "subject"` is present:** mode = `ad-hoc`, subject = value of flag. Skip Ideas/ resolution. Proceed to Step 1.
3. **Otherwise (idea mode):**
   - If empty: `Glob` `Ideas/*.md`, read first 20 lines of each to extract title, present all ideas, ask user to select. If none exist, exit.
   - Try exact match at `Ideas/{argument}.md` (strip `.md` extension first if present)
   - If no exact match, try case-insensitive substring match
   - Single fuzzy match → use it
   - Multiple fuzzy matches → present options, ask user to pick
   - Zero matches → **ERROR**: "Idea file not found: `{argument}`. Closest candidates in Ideas/: `{list up to 5}`. For ad-hoc analysis of a non-idea subject, use: `/educator-sme --adhoc \"{argument}\"`." Exit. Do NOT silently interpret as ad-hoc.

### Step 1: Load Context

**Idea mode:** Read the idea file at the resolved path — full content (frontmatter + body). Extract:

- **Core insight** — from the body content
- **Problem statement** — from `Problem it addresses` if present (Stage 2+), or infer from core insight (Stage 1)
- **Domain** — from frontmatter `domain` field, used for K-12 vs. higher ed calibration:
  - `assessments` — evaluate both K-12 and higher ed perspectives
  - `platform` — evaluate from downstream classroom impact
  - `cross-product` — evaluate both segments, note where they diverge

**Ad-hoc mode:** The subject string is the target. There is no idea file, no themes, no domain. Frame the evaluation around the subject itself (a product, tool, methodology, concept). Without a domain signal, evaluate both K-12 and higher ed perspectives unless the subject is clearly one or the other.

**Shared research baseline:** Query the strategy research database for customer evidence and educator-relevant findings:

```bash
python3 scripts/research-db.py query-landscape --json '{"capabilities": ["cap-slug-1", "cap-slug-2"]}'
```

Derive capability slugs from the idea's `themes` field. Within-TTL entries are known starting points for customer pain signals and adoption evidence — do not rediscover patterns already documented there. Past-TTL entries are directional only. During Step 4 (Optional Research), if web research surfaces a competitor or methodology, use `query-competitor` for a targeted deep-dive on what the database already knows about it.

Context exclusions (strategy docs, OKRs, persona guide, competitive data, business framing) are enforced by the agent's scope constraints.

### Step 2: Calibrate Perspective

Calibrate your perspective based on the idea's domain field using your domain calibration framework (K-12, higher ed, platform/infrastructure).

### Step 3: Evaluate (5 Dimensions)

Work through your five evaluation dimensions (Pain Point Validity, Adoption Realism, Workflow Integration, The Skeptic's Objection, The Champion's Argument) with educator-grounded specificity. Every claim must connect to a concrete classroom reality.

**Dimension-to-output mapping:**

- Pain Point Validity → "Pain Point Analysis" section
- Adoption Realism → "Adoption Assessment" verdict + "Adoption Barriers" section
- Workflow Integration → Folds into both "Pain Point Analysis" (current state) and "Adoption Barriers" (transition friction)
- The Skeptic's Objection → "What Would Make Educators Skeptical" section
- The Champion's Argument → "What Would Make Educators Champions" section

The "Strongest Use Case" and "Suggested Refinements" output sections synthesize across all five dimensions.

### Step 4: Optional Research

If the idea makes specific pedagogical claims or references methodologies that need validation, use `WebSearch` to check:

- Educator sentiment on the specific methodology (e.g., "teacher opinions on standards-based grading")
- Research on similar interventions and their adoption rates
- Adoption data for comparable edtech tools
- Educator community discussions (Reddit r/Teachers, education blogs, union publications)

Bound research to 3-6 targeted searches; stop when the artifact template's fields are covered.

If the idea is straightforward enough to evaluate from educator experience alone, skip this step and note "No external research needed — evaluation based on educator practice knowledge."

### Step 5: Write Research Artifact

**Ad-hoc mode:** Skip this step — no idea-scoped folder, no frontmatter to update. Jump to Step 6 with findings going to the database and conversation only.

**Idea mode:**

1. Use `Bash(date:*)` to get today's date in YYYY-MM-DD format
2. Create directory if needed: `Research/{idea-name}/` (Write tool auto-creates parents)
3. Write `Research/{idea-name}/educator-evaluation.md` — if a file already exists at this path from a prior run, write to `Research/{idea-name}/educator-evaluation-{YYYY-MM-DD}.md` instead; if that also exists, append `-2`, `-3`, etc., for same-day collisions.
4. Structure:

```markdown
---
type: incubator/research
research-type: educator-sme-evaluation
idea: {idea-name}
date: {YYYY-MM-DD}
domain-calibration: {k12 | higher-ed | both | platform-downstream}
---

# Educator SME Evaluation: {Idea Title}

**Evaluated:** {YYYY-MM-DD}
**Idea stage at evaluation:** {stage from frontmatter}
**Domain calibration:** {K-12 / Higher Ed / Both / Platform (downstream impact)}

## Adoption Assessment: {High / Medium / Low}
**Verdict:** {One direct sentence.}

## Pain Point Analysis
{2-3 sentences on problem reality and severity from an educator's daily experience.}

## Pedagogical Soundness / Student-Outcome Judgment
{Required — make the call explicitly, do not leave it implied. Does this reach the student, and how? Trace the path from the idea to a change in what a student experiences or learns. If the benefit lands on the institution — admin visibility, reporting, compliance, staff efficiency — and reaches the student only indirectly or not at all, say so plainly and name the gap. "Great for admin dashboards, invisible to the kid struggling with fractions" is a complete and acceptable verdict. Institutional benefit is not student benefit until the path is shown.}

## Adoption Barriers
{Specific friction points — concrete workflow realities, not abstractions. What specifically makes this hard to adopt?}

## What Would Make Educators Skeptical
{The eye-roll reaction. Be blunt. Channel the veteran teacher who's seen it all.}

## What Would Make Educators Champions
{The excitement moment. Be specific — describe the scenario, not the feature.}

## Strongest Use Case
{One concrete scenario: role, context, what happens, outcome. Make it vivid.}

## Suggested Refinements
{2-3 specific adjustments that address the barriers identified above. Actionable, not vague.}

## Research Notes
{If Step 4 was performed: queries, findings, sources. If skipped: "Evaluation based on educator practice knowledge — no external research needed."}
```

1. Update the idea file's frontmatter: append the written artifact path to the `research: []` array.
   - Read the idea file to get current frontmatter
   - Append the new path (including dated suffix if applicable from step 3)
   - Do NOT remove older dated-suffix entries from prior runs — augment artifacts coexist
   - Use `Edit` to update the frontmatter — find the `research:` line and update it
   - Do NOT modify any other frontmatter fields, body content, or the idea's stage

### Step 6: Present Results

**Idea mode:** Present the evaluation with the idea-name, impact dimension signals, and research artifact path.

**Ad-hoc mode:** Present the evaluation with the subject string. Omit impact dimension signals entirely. Omit research artifact path. DB findings still captured per Step 6's write-back section.

Idea-mode presentation template:

```text
Educator SME Evaluation: {idea-name}

**Adoption Assessment: {High / Medium / Low}**
{One-sentence verdict}

**Pain Point Analysis:**
{2-3 sentences}

**Adoption Barriers:**
{Specific friction points}

**The Skeptic Says:**
{Eye-roll reaction}

**The Champion Says:**
{Excitement moment}

**Strongest Use Case:**
{Concrete scenario}

**Suggested Refinements:**
{2-3 adjustments}

**Impact dimension signals:**
- Customer sentiment: {what this evaluation suggests — high/medium/low signal and why}
- User experience: {what this evaluation suggests — high/medium/low signal and why}

Research artifact written to: Research/{idea-name}/educator-evaluation.md
Idea frontmatter updated: research array now includes educator evaluation path.
```

After presenting the above, review your findings against the shared research capture heuristic: **Sourced + Durable + Decision-relevant + Shared** (applies to pain point evidence, adoption patterns, and educator sentiment that would benefit other ideas). Write qualifying findings to the strategy research database. **Source URL requirement:** Every finding MUST have a `source_url` with the most specific available page — not a homepage. Use `source_description` only when no stable URL exists. Do not write findings with neither.

**Claim-content guardrail:** A finding's `claim` field must be a **substantive assertion** with content the reader can act on. The following are NOT findings — never write them as `claim`:

- Search query strings (e.g., `"teacher experience using AI rubric generator 2025"`) — these are research metadata, not findings
- Bare citations / titles (e.g., `[Title](URL)`) — a citation without an assertion is a bookmark, not a finding
- Query-prefixed paragraphs where the leading quoted query is verbatim what you searched — strip the query; submit only the assertion

If research surfaced an article whose title is the most relevant signal, capture the article's *finding* as your `claim` (the assertion the article makes), with the article's URL as `source_url`. The title belongs at the URL's content, not in your `claim` field.

```bash
python3 scripts/research-db.py write-findings --json '{
  "findings": [
    {
      "claim": "...",
      "evidence": "...",
      "confidence": "high|medium|low",
      "source_url": "https://specific-page-url (REQUIRED — not a homepage)",
      "source_description": "fallback only when no stable URL exists",
      "ttl_months": 12,
      "topic": "customer-evidence",
      "category": "pain-signal|research-validation|adoption-signal",
      "capabilities": ["slug-1", "slug-2"],
      "competitor_id": null
    }
  ]
}'
```

Note: The impact dimension signals are advisory — they indicate what this evaluation suggests for the `customer-sentiment` and `user-experience` frontmatter fields, but this skill does NOT modify those fields. That's done during the development workflow or manually by the human.

Your impact-dimension signals are advisory. If a signal contradicts the idea card's existing frontmatter ratings, state the contradiction explicitly in your report — do not silently align to the card. The same applies to factual claims: if your research contradicts a factual claim in the card body, surface the contradiction prominently in your final report — not buried in the artifact — so the orchestrator can reconcile the card.

## Stop Rules

| Condition | Action |
| ----------- | -------- |
| Idea file not found | Fuzzy match attempt, then report available files and exit |
| Idea too abstract for educator lens | Report: "This idea is too abstract to evaluate from a classroom perspective. To proceed, ground it in a specific educator workflow or student outcome." Ask human to refine. |
| No meaningful educator touchpoint | Report: "This idea is pure infrastructure with no downstream classroom impact I can evaluate. The educator perspective doesn't apply here." Exit cleanly. |
| Research directory creation fails | Report the error and exit |
| Idea file has malformed frontmatter | Report parsing issue with specifics, exit |

## Error Handling Summary

| Condition | Behavior |
| ----------- | ---------- |
| No argument and no ideas exist | Report "No ideas found in Ideas/" and exit |
| Idea file not found | Report with available filenames from Ideas/ listing, exit |
| Frontmatter cannot be parsed | Report parsing issue, exit |
| Domain field missing from frontmatter | Default to "both" (K-12 and higher ed), note the assumption |
| Research directory already exists | Proceed — write/overwrite the evaluation file |
| Educator evaluation already exists for this idea | Write dated-suffix augment file per Step 5 (`educator-evaluation-{YYYY-MM-DD}.md`, counter for same-day); append new path to frontmatter; do not remove the original |
| WebSearch returns no relevant results | Note "No relevant educator sentiment found for {query}" and continue with practice-based evaluation |

## Scope Boundaries

This skill does NOT:

- Change the idea's stage (enrichment only)
- Modify the idea body content
- Modify impact dimension frontmatter fields (advisory signals only)
- Recommend go/no-go decisions (that's a human decision)
