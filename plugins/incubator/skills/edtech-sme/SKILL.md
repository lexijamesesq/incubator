---
name: edtech-sme
description: This skill should be used when the user asks to "get market analysis for [idea]", "edtech evaluation of [idea/subject]", "competitive analysis for [idea/subject]", "market perspective on [company/technology/concept]", or "edtech SME review of [subject]". Evaluates a strategic idea OR an arbitrary subject (competitor, technology, concept) against edtech market dynamics, competitive landscape, buyer behavior, and technology trends from an industry analyst perspective.
argument-hint: "[idea-name | idea-row-url | --adhoc \"subject\"] [notion_ideas=...] [notion_research=...] [notion_config=...]"
context: fork
agent: incubator:edtech-sme
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

# /edtech-sme — EdTech Market Analysis (Enrichment Agent)

Evaluates a strategic idea against edtech market dynamics, competitive landscape, buyer behavior, and technology trends. Produces a research artifact from an outside-in industry analyst perspective. This is an enrichment agent — it does NOT change the idea's stage.

## Invocation

```text
/edtech-sme [idea-name]                  # idea mode
/edtech-sme --adhoc "subject string"     # ad-hoc mode
```

Two modes:

- **Idea mode** (naked argument): the argument names an idea (its Slug in the Ideas database) or is the idea row's URL. Skill loads the idea and evaluates it. Writes its artifact as a row in the Research database (Research type `edtech-market-analysis`), related to the idea; that relation is what puts it on the idea's research list.
- **Ad-hoc mode** (`--adhoc "subject"`): the flag carries a free-form subject string (competitor, technology, concept). Skill evaluates the subject on its own. No artifact row, nothing written to Notion. Findings still write back to the research database.

Examples: `/edtech-sme foraging-intelligence`, `/edtech-sme --adhoc "Top Hat"`, `/edtech-sme --adhoc "adaptive learning platforms"`.

## Where Things Are (idea mode)

Ad-hoc mode reads no idea and writes nothing to Notion (its one possible Notion read is the Configuration page, for `role`). Idea mode reads and writes Notion, and how a skill does that is stated once, in `reference/skill-conventions-notion-access.md` in the Incubator repo: read it before Step 0 and follow it. If idea mode cannot read that file (the session is not in the Incubator repo and has no copy), stop and say so. Only what is specific to this skill is stated here.

- **Pointers (idea mode):** `notion_ideas`, `notion_research`; `notion_config`, where there is one, for `role`. A caller that has already fetched the Research database may pass `research_data_source=<collection:// URL>`. A pointer idea mode needs and does not have: report "Idea mode needs the {pointer} pointer (CLAUDE.md front matter, or a {pointer}= argument). For a subject that is not an idea, use --adhoc." and exit.
- **Rows it touches (idea mode):** reads the idea row; creates one Research row related to it, Research type `edtech-market-analysis`.

## Arguments

Parse `$ARGUMENTS` to determine mode. Every `key=value` token (`notion_ideas=`, `notion_research=`) is a pointer override, not the idea:

- If `--adhoc "subject"` present: **ad-hoc mode**, subject = value of flag. Skip idea resolution entirely.
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
| Zero matches | **ERROR** (see below) — never silently fall through to ad-hoc |

**Zero-match error text:**

> Idea not found: `{arg}`. Closest candidates in the Ideas database: `{list up to 5 slugs with lowest edit distance or shortest substring proximity}`. For ad-hoc analysis of a non-idea subject, use: `/edtech-sme --adhoc "{arg}"`.

Exit. Do NOT silently interpret a no-match as ad-hoc mode.

## Persona

This skill runs in the edtech-sme agent's context. The agent carries the full industry analyst persona, domain knowledge (competitors, buyer dynamics, dual-role entities), evaluation framework, and quality standards. See `.claude/agents/edtech-sme.md`.

**Invocation note:** When executed by a pointer-invoked agent rather than the Skill tool: run research-db.py from the project root.

**Output serves two purposes:**

- **Enrichment:** Feeds into the idea's `industry-disruption`, `revenue-potential`, and `strategic-alignment` impact dimension assessments
- **Research artifact:** Preserved as the idea's `edtech-market-analysis` Research row for reference during drafting and refining stages

## Execution Flow

Execute these steps in order. Stop and report errors at any step rather than continuing with bad data.

### Step 0: Parse Arguments

1. Read `$ARGUMENTS`. Detect `--adhoc` flag.
2. **If `--adhoc "subject"` is present:** mode = `ad-hoc`, subject = value of flag. Skip idea resolution. Proceed to Step 1.
3. **Otherwise (idea mode):** settle the pointers (an argument override where one is given, the `CLAUDE.md` front matter otherwise), then:
   - If the argument is a Notion row URL: fetch it and use it. If the database it is in is not `notion_ideas`, report and exit.
   - If empty: read the Ideas view. Present all ideas to the user (with their Stage) and ask them to select one Leave out rows at Stage `archived`. If no ideas exist, report "No ideas found in the Ideas database" and exit.
   - Try exact match on the Slug field (strip `.md` extension first if present)
   - If no exact match, try case-insensitive substring match against the Slug and Name of all rows
   - Single fuzzy match → use it
   - Multiple fuzzy matches → present options, ask user to pick
   - Zero matches → **ERROR**: "Idea not found: `{argument}`. Closest candidates in the Ideas database: `{list up to 5}`. For ad-hoc analysis of a non-idea subject, use: `/edtech-sme --adhoc \"{argument}\"`." Exit. Do NOT silently interpret as ad-hoc.

### Step 1: Load Context

**Idea mode:** Fetch the idea row (unless Step 0 already did) — one fetch returns its fields and its full body. Extract:

- **Core insight** — the central idea being evaluated
- **Themes** — from the `Themes` field
- **Domain** — from the `Domain` field
- **Stage** — from the `Stage` field (for reporting, not gating)
- **Existing research** — the rows in the `Research` relation (to avoid duplicating work)

**Ad-hoc mode:** The subject string is the target. There is no idea row, no themes, no domain, no prior research. Frame the evaluation around the subject itself — the company, technology, or concept — rather than an idea being evaluated against the market.

**Company context (both modes):** the agent reads the company and its position from the Configuration key `role`. If the instruction file's front matter names `notion_config`, or a `notion_config=` argument is given, fetch that page and read `role` from its `yaml` block. Otherwise use the Configuration section of the project's instruction file, already in context.

**Shared research baseline:**

- **Idea mode:** Query by capability slugs derived from the idea's `Themes` field:

  ```bash
  python3 scripts/research-db.py query-landscape --json '{"capabilities": ["cap-slug-1", "cap-slug-2"]}'
  ```

- **Ad-hoc mode:** Look up the subject directly. If the subject names a company/product, try `lookup-competitor`:

  ```bash
  python3 scripts/research-db.py lookup-competitor --json '{"name": "Subject Name"}'
  python3 scripts/research-db.py query-competitor --json '{"name": "Subject Name"}'
  ```

  If no match, query by inferred capability slugs if any apply, otherwise proceed with web research only.

Within-TTL entries are known starting points — do not rediscover competitors already documented there. Past-TTL entries are directional only (relevant categories and framing, not current positioning). During Step 3, use `query-competitor` for targeted deep-dives on competitors central to the analysis.

**Competitor registry:** Snowflake `competitors` table — accessed via `query-landscape` (Step 1 above) which returns name, category, market_tier, pricing_model, and matched capabilities filtered by capability slug. For deeper context on a specific competitor central to the analysis, use `query-competitor --json '{"name": "..."}'`.

Context exclusions (strategy docs, OKRs, persona guide, approach docs) are enforced by the agent's scope constraints.

### Step 2: Frame Market Lens

Before researching, frame the idea through your market lens — product category, buyer, competitive frame, and technology bets.

If the idea spans multiple product categories, identify all relevant categories for expanded competitor scanning.

If the idea is too abstract for market analysis — no discernible product concept, buyer, or competitive frame — fire the stop rule (see Stop Rules section).

### Step 3: Research Competitive Landscape

Use `WebSearch` to gather current market intelligence. Execute 4-6 targeted searches derived from the idea's themes, competitive frame, and product category.

**Search targets:**

- **Registry-informed targeted searches:** For each registry-matched competitor (from Step 1), include at least one targeted search for that competitor's recent activity in the idea's capability domain. E.g., if the idea is about rubric design and FeedbackFruits is registry-matched, search for "FeedbackFruits rubric" or "FeedbackFruits assessment authoring 2025 2026". These targeted searches supplement — not replace — the generic searches below.
- Competitor features and recent product launches in the relevant category
- Acquisitions, mergers, and strategic partnerships in edtech assessment
- Analyst commentary (EdSurge, EdTech Magazine, Gartner, HolonIQ)
- Regulatory developments (state/federal assessment mandates, accessibility requirements, AI policy in education)
- Platform shifts and technology trends (AI in assessment, interoperability standards like QTI/LTI, competency-based education movement)

**When the idea spans multiple product categories**, expand the competitor scan to include adjacent-category players. Name specific companies from each relevant category — do not limit to direct assessment competitors.

**Research quality standards:**

- Name competitors, cite specific products, reference real dynamics
- Capture source URLs for all findings
- Flag any knowledge that is more than 18 months old
- Prioritize depth over breadth — 4 strong findings beat 8 shallow ones

**Cross-idea awareness:** If your competitive research reveals that the same competitor landscape applies to another idea you've seen in the Ideas view (when the argument resolution step read it), note it in the artifact: "Competitive overlap: similar landscape applies to [other-idea-name]." This is informational only — do not modify the other idea's row.

If `WebSearch` returns no relevant results for a query, note it and try an alternative search angle. If no competitive data is found across all searches, proceed with low-confidence flags (see Error Handling).

### Step 4: Evaluate (4 Dimensions)

Using the idea context and research findings, evaluate across your four dimensions: Market Fit, Competitive Positioning, Technology Risk, and Go-to-Market.

For Competitive Positioning, build a competitor comparison table with specific companies, their relevant capabilities, and how your organization would compare (Differentiation / Parity / Behind). Write a positioning narrative: 2-3 sentences on where your organization lands.

For Technology Risk, rate as Low / Medium / High. For ideas with emerging technology themes, explicitly assess the gap between current capability and institutional deployment readiness.

### Step 5: Assess Strategic Timing

Analyze the market window with specific signals:

- Is the market moving toward this idea or away from it?
- What external forces (regulatory, technological, competitive) create urgency or reduce it?
- Is there a first-mover advantage, or is fast-follower safer?
- Specific timing signals: funding cycles, regulatory deadlines, competitor roadmap signals, technology maturity curves

### Step 6: Write Research Artifact

**Ad-hoc mode:** Skip this step entirely — there is no idea to relate an artifact to. Jump to Step 7 (present results) with findings going to the database and conversation only.

**Idea mode:**

1. Get today's date using `Bash(date:*)`: `date +%Y-%m-%d` (the local date)
2. Create the artifact as a new row in the Research database with one `notion-create-pages` call (`allow_async` false, so the row's URL comes back). A row of this type may already exist for the idea from a prior run: do not look for it and do not change it. Every run creates a new row dated today, and earlier rows stay.

**Row parent:** the Research data source — the `collection://` URL passed as `research_data_source=` when a caller gave one; otherwise fetch the `notion_research` database and take the data source it lists.

**Row fields** (these replace the artifact file's front matter):

| Field | Value |
| --- | --- |
| `Name` | `EdTech Market Analysis: {Idea Title}` |
| `Idea` | a one-item array holding the idea row's URL |
| `Research type` | `edtech-market-analysis` |
| `Agent` | `edtech-sme` |
| `date:Created:start` | today, `YYYY-MM-DD` (with `date:Created:is_datetime` 0) |
| `Confidence` | `high`, `medium` or `low` |

Never write a value outside a field's options. If Notion refuses the create because a field lacks the option, report which option is missing and present the analysis in the output; do not create the row under another value.

**Run under `/thesis-test`.** When the caller's execution contract names another Research type and Name for the artifact row (`/thesis-test` does: `thesis-test-lens`, `thesis-test-{lens}-{date} ({slug})`) and a verdict record for its body, create the row with those in place of the type, Name and body template here. Parent, `Idea`, `Created` and the rest are unchanged.

**Row body** (the artifact; its title is the row's Name and is not repeated):

```markdown
**Idea:** {Core insight from the idea row}
**Analysis date:** {YYYY-MM-DD}
**Confidence level:** {High/Medium/Low — High: strong data across all dimensions. Medium: gaps in 1-2 dimensions. Low: thin data, limited competitive intelligence.}

## Market Fit Assessment: {Strong / Moderate / Weak}

{One-sentence verdict.}

{2-4 sentences of supporting analysis. Buyer-centric: willingness to pay, not product excitement. Reference specific market signals.}

## Competitive Positioning

| Competitor | Relevant Capability | Comparison |
|------------|---------------------|------------|
| {Name} | {What they do} | {Differentiation / Parity / Behind} |

**Positioning narrative:** {2-3 sentences. Where your organization lands relative to competitors. Honest assessment.}

## Technology Risk: {Low / Medium / High}

{2-3 specific sentences. Maturity for institutional deployment, integration requirements, build/buy/partner considerations.}

## Go-to-Market Considerations

{3-4 sentences: buyer alignment, pricing model, sales channel, regulatory factors.}

## Strategic Timing

{2-3 sentences on market window. Specific signals — regulatory deadlines, competitor moves, technology maturity, funding cycles.}

## Key Risks

- {Specific market risk 1}
- {Specific market risk 2}
- {Specific market risk 3}
- {Specific market risk 4 — if applicable}

## Opportunity Signal Strength: {Strong / Moderate / Weak}

{One synthesizing sentence connecting market fit, competitive positioning, technology risk, and timing to overall opportunity quality. Connect to MAU x ARPU = ARR where applicable.}

## Research Sources

- {Source 1 with URL}
- {Source 2 with URL}
- {Source 3 with URL}
```

1. The idea's research list is its `Research` relation, and setting `Idea` on the new row is what adds the artifact to it. Make no write to the idea row.

   **Research-list rules:**
   - Do not remove or change earlier rows of this type from prior runs — they coexist
   - Do NOT change any field of the idea row (especially `Stage`), or its body
   - Keep the URL the create returned: it is the artifact reference Step 7 reports

### Step 7: Present Results

**Idea mode:** Present the completed analysis with the idea-name, impact dimension implications (for /develop synthesis), and the research artifact row's URL.

**Ad-hoc mode:** Present the analysis with the subject string, omit impact dimension implications entirely, omit the research artifact reference. Findings still go to the database.

Idea-mode presentation template:

```text
EdTech market analysis complete: {idea-name}

**Market Fit:** {Strong/Moderate/Weak} — {one-sentence verdict}

**Top Competitors:**
- {Competitor 1}: {capability} — {Differentiation/Parity/Behind}
- {Competitor 2}: {capability} — {Differentiation/Parity/Behind}
- {Competitor 3}: {capability} — {Differentiation/Parity/Behind}

**Technology Risk:** {Low/Medium/High} — {one-sentence summary}

**Key Risks:**
- {Risk 1}
- {Risk 2}

**Opportunity Signal Strength:** {Strong/Moderate/Weak} — {synthesizing sentence}

**Impact dimension implications:**
- industry-disruption: {Suggested Low/Med/High based on competitive positioning}
- revenue-potential: {Suggested Low/Med/High based on market fit and go-to-market}
- strategic-alignment: {Suggested Low/Med/High based on timing and market direction}

**Research artifact:** {URL of the artifact row}
**Confidence:** {High/Medium/Low}
```

Your impact-dimension signals are advisory. If a signal contradicts the idea card's existing ratings (the row's impact-dimension fields), state the contradiction explicitly in your report — do not silently align to the card. The same applies to factual claims: if your research contradicts a factual claim in the card body, surface the contradiction prominently in your final report — not buried in the artifact — so the orchestrator can reconcile the card.

After presenting the above, review your findings against the shared research capture heuristic: **Sourced + Durable + Decision-relevant + Shared** (applies to competitor entries, market dynamics, and positioning data that would benefit other ideas). Write qualifying findings to the strategy research database:

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
      "topic": "competitive-landscape",
      "category": "capability-specific|capability-presence|competitive-gap",
      "capabilities": ["slug-1", "slug-2"],
      "competitor_id": "uuid-or-null"
    }
  ]
}'
```

**Source URL requirement:** Every finding MUST have a `source_url` with the most specific available page — not a homepage. Use `source_description` only when no stable URL exists, with enough detail to locate the source. Do not write findings with neither.

Use `python3 scripts/research-db.py lookup-competitor --json '{"name": "..."}'` to resolve competitor names to IDs. When a web search finding relates to a competitor already in the database, link it. When web research sparks a question about what the database already knows, query for it:

```bash
python3 scripts/research-db.py query-competitor --json '{"name": "Competitor Name"}'
```

This oscillation between web research and database lookups produces richer context than either source alone.

**Competitor registry updates:**

Update the competitor registry via `upsert-competitor`:

```bash
python3 scripts/research-db.py upsert-competitor --json '{
  "name": "Competitor Name",
  "category": "core|adjacent|emerging|substitute",
  "segments": ["k-12", "higher-ed"],
  "market_tier": "tier-1|tier-2|tier-3",
  "pricing_model": "per-seat|platform-fee|...",
  "integration_posture": ["lti-certified"],
  "capabilities": ["slug-1", "slug-2"],
  "intelligence_body": "Substantive 2-5 sentence positioning narrative (min 50 chars)...",
  "source_url": "https://specific-page (REQUIRED for new entries — not a homepage)"
}'
```

- **New competitors:** The command's fuzzy-name dup check returns candidates if any look similar; if the new competitor is genuinely distinct, re-run with `force_create: true`. Evidence requirement: `source_url` or `source_description` is mandatory for inserts.
- **Existing competitors:** Run the same command — exact-name lookup hits the existing row and updates the fields you provide. Skip a field to leave it untouched. `last_researched` stamps automatically.
- **Category changes:** The command rejects a category change with `action: needs_category_confirmation`. Surface the proposal to the human in the presentation. The skill never passes `force_category_change: true` — that flag is reserved for human-initiated invocations.
- **Found-superseded:** If the command returns `action: found_superseded` (the name exists but is soft-deleted/self-superseded), surface to the human with the message text. The skill never auto-revives a superseded row.

Note in the presentation:
> **Competitor registry updated:** +{N} new files, {N} updated ({brief descriptions})

## Stop Rules

| Condition | Action |
| --- | --- |
| Idea too abstract for market analysis (no discernible product concept, buyer, or competitive frame) | Report: "This idea is too abstract for market analysis. To evaluate market dynamics, I need a clearer product concept — what would the buyer be purchasing?" Ask human to refine before rerunning. Exit. |
| No competitive data found across all searches | Proceed with low-confidence flags on all dimensions. Write artifact noting data limitations. Present results with explicit confidence warnings. |

**Note:** Unlike the Development Session Workflow, this agent does NOT have stop rules for weak ideas or thin strategic connections. The EdTech SME evaluates whatever it receives — a weak market fit is a valid finding, not a reason to stop. Even ideas with no competitive landscape or unclear product concepts get an honest "Weak" assessment rather than a refusal to evaluate.

## Error Handling

| Condition | Behavior |
| ----------- | ---------- |
| No argument and no ideas exist | Report "No ideas found in the Ideas database" and exit |
| Idea not found | Fuzzy match against the Slug and Name of the Ideas rows. If no match, report with available slugs and exit |
| Idea mode with a pointer missing | Report which pointer is missing and that `--adhoc` needs none. Exit. |
| Idea too abstract for market lens | Report what is missing (product concept, buyer persona, competitive frame) and ask human for refinement. Exit. |
| No competitive data available | Write artifact with low confidence flags on all dimensions. Note data limitations explicitly in each section. |
| WebSearch returns no results for a query | Note the failed query, try alternative search angle. If all searches fail, proceed with low confidence. |
| Artifact row creation fails | Report error with specifics, present the analysis in the output so the work is not lost, exit |
| The created row does not show the idea in its `Idea` relation | Report error, give the row's URL, note the artifact was written and the relation needs setting by hand. Exit. |

## Scope Boundaries

This skill does NOT:

- Change the idea's stage (enrichment only)
- Modify the idea row's body or fields (its only trace on the idea is the new artifact row in the `Research` relation)
- Recommend go/no-go decisions (that is a human decision)
