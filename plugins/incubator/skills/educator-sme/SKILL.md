---
name: educator-sme
description: This skill should be used when the user asks to "get educator feedback on [idea]", "educator evaluation of [idea/subject]", "teacher perspective on [idea/subject]", "classroom reality check for [idea]", or "educator SME review of [subject]". Evaluates a strategic idea OR an arbitrary subject (product, tool, methodology) through the lens of a veteran educator — 20+ years K-12 and higher ed — focused on pedagogical practice, classroom reality, and adoption likelihood.
argument-hint: "[idea-name | idea-row-url | --adhoc \"subject\"] [notion_ideas=...] [notion_research=...]"
context: fork
agent: incubator:educator-sme
disable-model-invocation: false
allowed-tools:
  - Read
  - WebSearch
  - WebFetch
  - Bash(date:*)
  - Bash(python3 scripts/research-db.py:*)
  - mcp__notion__notion-fetch
  - mcp__notion__notion-query-data-sources
  - mcp__notion__notion-create-pages
---

# /educator-sme — Educator SME Evaluation

Evaluates a strategic idea through the lens of a veteran educator with 20+ years spanning K-12 and higher ed. Produces an unfiltered assessment of pain point validity, adoption realism, and classroom impact. This is an enrichment agent — it adds a research artifact without changing the idea's stage.

## Invocation

```text
/educator-sme [idea-name]                  # idea mode
/educator-sme --adhoc "subject string"     # ad-hoc mode
```

Two modes:

- **Idea mode** (naked argument — an idea's Slug, or the idea row's URL): evaluates an idea. Writes its artifact as a row in the Research database (Research type `educator-sme-evaluation`), related to the idea; that relation is what puts it on the idea's research list.
- **Ad-hoc mode** (`--adhoc "subject"`): evaluates a free-form subject (product, tool, methodology). No artifact row, nothing written to Notion. DB findings still captured.

Examples: `/educator-sme foraging-intelligence`, `/educator-sme --adhoc "Top Hat"`, `/educator-sme --adhoc "standards-based grading"`.

## Where Things Are (idea mode)

Ad-hoc mode makes no Notion call. Idea mode reads and writes Notion, and how a skill does that is stated once, in `reference/skill-conventions-notion-access.md` in the Incubator repo: read it before Step 0 and follow it. If idea mode cannot read that file (the session is not in the Incubator repo and has no copy), stop and say so. Only what is specific to this skill is stated here.

- **Pointers (idea mode):** `notion_ideas`, `notion_research`. A caller that has already fetched the Research database may pass `research_data_source=<collection:// URL>`. A pointer idea mode needs and does not have: report "Idea mode needs the {pointer} pointer (CLAUDE.md front matter, or a {pointer}= argument). For a subject that is not an idea, use --adhoc." and exit.
- **Rows it touches (idea mode):** reads the idea row; creates one Research row related to it, Research type `educator-sme-evaluation`.

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
| Zero matches | **ERROR**: "Idea not found: `{arg}`. Closest candidates in the Ideas database: `{list up to 5 slugs}`. For ad-hoc analysis of a non-idea subject, use: `/educator-sme --adhoc \"{arg}\"`." Exit. Do NOT silently fall through to ad-hoc. |

## Persona

This skill runs in the educator-sme agent's context. The agent carries the full veteran educator persona (20+ years K-12 and higher ed), domain calibration framework, evaluation dimensions, and quality standards. See `.claude/agents/educator-sme.md`.

**Invocation note:** When executed by a pointer-invoked agent rather than the Skill tool: run research-db.py from the project root.

## Execution Flow

Execute these steps in order. Stop and report errors at any step rather than continuing with bad data.

### Step 0: Parse Arguments

1. Read `$ARGUMENTS`. Detect `--adhoc` flag.
2. **If `--adhoc "subject"` is present:** mode = `ad-hoc`, subject = value of flag. Skip idea resolution. Proceed to Step 1.
3. **Otherwise (idea mode):** settle the pointers (an argument override where one is given, the `CLAUDE.md` front matter otherwise), then:
   - If the argument is a Notion row URL: fetch it and use it. If the database it is in is not `notion_ideas`, report and exit.
   - If empty: read the Ideas view, present all ideas by Name, ask user to select Leave out rows at Stage `archived`. If none exist, exit.
   - Try exact match on the Slug field (strip `.md` extension first if present)
   - If no exact match, try case-insensitive substring match against the Slug and Name of all rows
   - Single fuzzy match → use it
   - Multiple fuzzy matches → present options, ask user to pick
   - Zero matches → **ERROR**: "Idea not found: `{argument}`. Closest candidates in the Ideas database: `{list up to 5}`. For ad-hoc analysis of a non-idea subject, use: `/educator-sme --adhoc \"{argument}\"`." Exit. Do NOT silently interpret as ad-hoc.

### Step 1: Load Context

**Idea mode:** Fetch the idea row (unless Step 0 already did) — one fetch returns the full content (fields + body). Extract:

- **Core insight** — from the body content
- **Problem statement** — from `Problem it addresses` if present (Stage 2+), or infer from core insight (Stage 1)
- **Domain** — from the `Domain` field, used for K-12 vs. higher ed calibration:
  - `assessments` — evaluate both K-12 and higher ed perspectives
  - `platform` — evaluate from downstream classroom impact
  - `cross-product` — evaluate both segments, note where they diverge

**Ad-hoc mode:** The subject string is the target. There is no idea row, no themes, no domain. Frame the evaluation around the subject itself (a product, tool, methodology, concept). Without a domain signal, evaluate both K-12 and higher ed perspectives unless the subject is clearly one or the other.

**Shared research baseline:** Query the strategy research database for customer evidence and educator-relevant findings:

```bash
python3 scripts/research-db.py query-landscape --json '{"capabilities": ["cap-slug-1", "cap-slug-2"]}'
```

Derive capability slugs from the idea's `Themes` field. Within-TTL entries are known starting points for customer pain signals and adoption evidence — do not rediscover patterns already documented there. Past-TTL entries are directional only. During Step 4 (Optional Research), if web research surfaces a competitor or methodology, use `query-competitor` for a targeted deep-dive on what the database already knows about it.

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

**Ad-hoc mode:** Skip this step — there is no idea to relate an artifact to. Jump to Step 6 with findings going to the database and conversation only.

**Idea mode:**

1. Use `Bash(date:*)` to get today's date in YYYY-MM-DD format (`date +%Y-%m-%d`, the local date)
2. Create the artifact as a new row in the Research database with one `notion-create-pages` call (`allow_async` false, so the row's URL comes back). A row of this type may already exist for the idea from a prior run: do not look for it and do not change it. Every run creates a new row dated today, and earlier rows stay.
3. Row parent: the Research data source — the `collection://` URL passed as `research_data_source=` when a caller gave one; otherwise fetch the `notion_research` database and take the data source it lists.
4. Row fields (these replace the artifact file's front matter), then the body structure:

| Field | Value |
| --- | --- |
| `Name` | `Educator SME Evaluation: {Idea Title}` |
| `Idea` | a one-item array holding the idea row's URL |
| `Research type` | `educator-sme-evaluation` |
| `date:Created:start` | today, `YYYY-MM-DD` (with `date:Created:is_datetime` 0) |
| `Domain calibration` | `k12`, `higher-ed`, `both` or `platform-downstream` |

Never write a value outside a field's options. If Notion refuses the create because a field lacks the option, report which option is missing and present the evaluation in the output; do not create the row under another value.

**Run under `/thesis-test`.** When the caller's execution contract names another Research type and Name for the artifact row (`/thesis-test` does: `thesis-test-lens`, `thesis-test-{lens}-{date} ({slug})`) and a verdict record for its body, create the row with those in place of the type, Name and body template here. Parent, `Idea`, `Created` and the rest are unchanged.

The row body (the artifact; its title is the row's Name and is not repeated):

```markdown
**Evaluated:** {YYYY-MM-DD}
**Idea stage at evaluation:** {the idea row's Stage}
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

1. The idea's research list is its `Research` relation, and setting `Idea` on the new row is what adds the artifact to it. Make no write to the idea row.
   - Do not remove or change earlier rows of this type from prior runs — they coexist
   - Do NOT modify any field of the idea row, its body, or the idea's stage
   - Keep the URL the create returned: it is the artifact reference Step 6 reports

### Step 6: Present Results

**Idea mode:** Present the evaluation with the idea-name, impact dimension signals, and the research artifact row's URL.

**Ad-hoc mode:** Present the evaluation with the subject string. Omit impact dimension signals entirely. Omit the research artifact reference. DB findings still captured per Step 6's write-back section.

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

Research artifact written to: {URL of the artifact row}
Idea research list updated: the Research relation now includes the educator evaluation row.
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

Note: The impact dimension signals are advisory — they indicate what this evaluation suggests for the `Customer sentiment` and `User experience` fields of the idea row, but this skill does NOT modify those fields. That's done during the development workflow or manually by the human.

Your impact-dimension signals are advisory. If a signal contradicts the idea card's existing ratings (the row's impact-dimension fields), state the contradiction explicitly in your report — do not silently align to the card. The same applies to factual claims: if your research contradicts a factual claim in the card body, surface the contradiction prominently in your final report — not buried in the artifact — so the orchestrator can reconcile the card.

## Stop Rules

| Condition | Action |
| ----------- | -------- |
| Idea not found | Fuzzy match attempt, then report available slugs and exit |
| Idea too abstract for educator lens | Report: "This idea is too abstract to evaluate from a classroom perspective. To proceed, ground it in a specific educator workflow or student outcome." Ask human to refine. |
| No meaningful educator touchpoint | Report: "This idea is pure infrastructure with no downstream classroom impact I can evaluate. The educator perspective doesn't apply here." Exit cleanly. |
| Artifact row creation fails | Report the error, present the evaluation in the output so the work is not lost, and exit |
| Idea row cannot be read | Report the issue with specifics, exit |

## Error Handling Summary

| Condition | Behavior |
| ----------- | ---------- |
| No argument and no ideas exist | Report "No ideas found in the Ideas database" and exit |
| Idea not found | Report with available slugs from the Ideas view, exit |
| Idea mode with a pointer missing | Report which pointer is missing and that `--adhoc` needs none, exit |
| Idea row's fields cannot be read | Report the issue, exit |
| `Domain` field empty | Default to "both" (K-12 and higher ed), note the assumption |
| Educator evaluation already exists for this idea | Create a new row dated today per Step 5; it joins the idea's Research relation; do not change or remove the earlier row |
| WebSearch returns no relevant results | Note "No relevant educator sentiment found for {query}" and continue with practice-based evaluation |

## Scope Boundaries

This skill does NOT:

- Change the idea's stage (enrichment only)
- Modify the idea body content
- Modify the idea row's impact dimension fields (advisory signals only)
- Recommend go/no-go decisions (that's a human decision)
