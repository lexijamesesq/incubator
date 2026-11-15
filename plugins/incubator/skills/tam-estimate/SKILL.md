---
name: tam-estimate
description: This skill should be used when the user asks to "estimate TAM for [idea]", "size the market for [idea/subject]", "market sizing for [idea/subject]", "TAM analysis for [idea]", or "TAM estimate for [market category]". Produces defensible TAM/SAM/SOM estimates using top-down and bottom-up methodologies for a strategic idea OR an arbitrary market category/segment in the assessment/edtech space.
argument-hint: "[idea-name | idea-row-url | --adhoc \"market category\"] [notion_ideas=...] [notion_research=...] [notion_config=...]"
context: fork
agent: tam-estimate
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

# /tam-estimate — TAM Estimation Enrichment Agent

Produces defensible TAM/SAM/SOM estimates for a strategic idea in the assessment/edtech space. Uses top-down and bottom-up methodologies, reconciles divergence, and writes a research artifact. This is an enrichment agent — it does not change the idea's stage.

## Invocation

```text
/tam-estimate [idea-name]                  # idea mode
/tam-estimate --adhoc "market category"    # ad-hoc mode
```

Two modes:

- **Idea mode** (naked argument — an idea's Slug, or the idea row's URL): sizes the market for an idea. Writes its artifact as a row in the Research database (Research type `tam-estimate`), related to the idea; that relation is what puts it on the idea's research list.
- **Ad-hoc mode** (`--adhoc "subject"`): sizes a free-form market category/segment. No artifact row, nothing written to Notion. Findings still write back to the research database.

Examples: `/tam-estimate foraging-intelligence`, `/tam-estimate --adhoc "AI grading tools"`, `/tam-estimate --adhoc "K-12 authentic assessment"`.

## Where Things Are (idea mode)

Ad-hoc mode reads no idea and writes nothing to Notion (its one possible Notion read is the Configuration page, for `role`). In idea mode the idea is a row in the Ideas database, and the artifact this skill writes is a row in the Research database related to that idea (Research type `tam-estimate`). The shared mechanics — the pointers and their overrides, addressing an idea, creating an artifact row, how Notion returns text — are stated once in `reference/skill-conventions-notion-access.md` in the Incubator repo; read it before Step 0 when it is present. In short:

- **Pointers.** `notion_ideas` and `notion_research` are database URLs in the front matter of the instruction file (`CLAUDE.md`) of the project the session runs in. `notion_ideas=` and `notion_research=` arguments override them; a test run passes scratch databases this way. A caller that has already fetched the Research database may also pass `research_data_source=<collection:// URL>`, the parent for the artifact row. If idea mode has neither an argument nor a front-matter value for a pointer it needs, report "Idea mode needs the {pointer} pointer (CLAUDE.md front matter, or a {pointer}= argument). For a subject that is not an idea, use --adhoc." and exit.
- **Calls.** `notion-fetch` for a row or a database; `notion-query-data-sources` in view mode only (fetch the database, query the view it lists, page while `has_more`); `notion-create-pages` with a data-source parent to create the artifact row. Never SQL or rows mode.
- **Text.** Notion returns bold as `<b>`, a line break inside a paragraph as `<br />`, and `~`, `$`, `[ ]` escaped. The words are preserved; read through the markup.

## Arguments

Parse `$ARGUMENTS` to determine mode. Every `key=value` token (`notion_ideas=`, `notion_research=`) is a pointer override, not the idea:

- If `--adhoc "subject"` present: **ad-hoc mode**, subject = value of flag. Skip idea resolution.
- Otherwise: **idea mode**, naked argument = candidate idea name, or the idea row's URL.

**Idea-mode resolution (fail-closed):**

| Input | Behavior |
| ------- | ---------- |
| Empty | Read the Ideas view, present titles, ask user to select |
| A Notion row URL | The idea row, as `/develop` and other skills pass it. Fetch it; do not read the Ideas view. |
| `idea-name` or `idea-name.md` | Exact match on the Slug field (strip `.md` first) |
| No exact match | Case-insensitive substring match against the Slug and Name of all rows |
| Single fuzzy match | Use it |
| Multiple fuzzy matches | Present options, ask user to pick |
| Zero matches | **ERROR**: "Idea not found: `{arg}`. Closest candidates in the Ideas database: `{list up to 5 slugs}`. For ad-hoc market sizing, use: `/tam-estimate --adhoc \"{arg}\"`." Exit. Do NOT silently fall through to ad-hoc. |

## Persona

This skill runs in the tam-estimate agent's context. The agent carries the full market sizing analyst persona, domain knowledge (products, segments, geography, business model), SOM cap rules, divergent analyst mode, and quality standards. See `.claude/agents/tam-estimate.md`.

**Invocation note:** When executed by a pointer-invoked agent rather than the Skill tool: run research-db.py from the project root.

Output feeds into the `revenue-potential` impact dimension and supports investment prioritization conversations with VPs and ELT.

## Execution Flow

Execute these steps in order. Stop and report errors at any step rather than continuing with bad data.

### Step 0: Parse Arguments

1. Read `$ARGUMENTS`. Detect `--adhoc` flag.
2. **If `--adhoc "subject"` is present:** mode = `ad-hoc`, subject = value of flag. Skip idea resolution. Proceed to Step 1.
3. **Otherwise (idea mode):** settle the pointers (an argument override where one is given, the `CLAUDE.md` front matter otherwise), then:
   - If the argument is a Notion row URL: fetch it and use it. If the database it is in is not `notion_ideas`, report and exit.
   - If empty: read the Ideas view (its rows carry Stage, Domain and Themes), present all ideas with stage, ask user to select. If none exist, exit.
   - Try exact match on the Slug field (strip `.md` first)
   - If no exact match, case-insensitive substring match against the Slug and Name of all rows
   - Single fuzzy match → use it
   - Multiple fuzzy matches → present options, ask user to pick
   - Zero matches → **ERROR**: "Idea not found: `{argument}`. Closest candidates in the Ideas database: `{list up to 5}`. For ad-hoc market sizing, use: `/tam-estimate --adhoc \"{argument}\"`." Exit. Do NOT silently fall through to ad-hoc.

### Step 1: Load Context

**Idea mode:** Fetch the idea row (unless Step 0 already did) — one fetch returns the full content (fields + body). Extract:

- `Domain` field — assessments, platform, or cross-product
- `Themes` field — thematic keywords for search targeting
- **Core insight** — from body content
- **Problem it addresses** — from body content (if populated; may not exist at seed stage)

**Ad-hoc mode:** The subject string is the market category to size. No idea row, no themes, no domain. Frame Step 2 market scope entirely from the subject string. Ad-hoc subjects are expected to be reasonably specific (e.g., "K-12 authentic assessment" not "edtech"); if the subject is too broad, Step 2's stop rule fires.

**Company context (both modes):** the agent reads the company and its position from the Configuration key `role`. If the instruction file's front matter names `notion_config`, or a `notion_config=` argument is given, fetch that page and read `role` from its `yaml` block. Otherwise use the Configuration section of the project's instruction file, already in context.

**Shared research baseline:** Query the strategy research database for TAM figures, growth rates, and buyer benchmarks:

```bash
python3 scripts/research-db.py query-landscape --json '{"capabilities": ["cap-slug-1", "cap-slug-2"]}'
```

Derive capability slugs from the idea's `Themes` field. Within-TTL entries are known starting points — do not re-research established sizing data that is already documented and current. Past-TTL entries are directional only (useful for market category framing, not current figures).

No other rows or files needed. TAM estimation is externally validated — internal strategy docs are not relevant.

### Step 2: Define Market Scope

Based on the idea's domain and themes, define precisely what market is being sized. This is the foundation — everything downstream depends on a clear market definition.

**Domain-to-market mapping:**

| Domain | Primary Market Scope |
| -------- | --------------------- |
| `assessments` | K-12 assessment tools, higher ed assessment tools, or cross-segment assessment depending on themes |
| `platform` | LMS platform, integration/interoperability layer, analytics platform |
| `cross-product` | Multiple segments — size each independently then combine |

**Scoping rules:**

- State the market definition explicitly before any estimation
- Define what is IN scope and what is OUT of scope
- If the idea targets a specific segment (e.g., K-12 only), do not size the full education market
- If the idea spans segments, size each and show how they combine

**Platform/infrastructure ideas:** Apply your divergent analyst mode — size the enabling market rather than the direct product market. Present both direct and indirect revenue impact.

**Stop rule:** If the idea is too abstract to define a market scope (e.g., "make assessments better" with no specificity on what, for whom, or how), stop and ask the human to refine the idea before proceeding.

Present the market definition to confirm scope before proceeding to estimation. Format:

> **Market definition:** [Precise statement of what market is being sized]
> **In scope:** [Segments, geographies, buyer types included]
> **Out of scope:** [What is excluded and why]
>
> Proceeding with estimation. If this scope is wrong, interrupt now.

### Step 3: Top-Down Estimation

Start with the broadest relevant market and apply successive filters to arrive at TAM, SAM, and SOM.

**Methodology:**

1. Identify the broadest market category (e.g., global EdTech, global assessment market, K-12 digital learning)
2. Apply successive filters — each with a cited source:
   - Geography (e.g., North America share of global market)
   - Segment (e.g., K-12 vs. higher ed vs. corporate)
   - Category (e.g., assessment vs. LMS vs. content)
   - Buyer type (e.g., institutional vs. consumer)
3. Arrive at TAM (total addressable market for this category)
4. Apply SAM filters (serviceable — what your organization could realistically compete for given product scope, buyer relationships, geography)
5. Apply SOM filters (obtainable — realistic capture given current market position, sales capacity, competitive dynamics)

**Search strategy:**

- Use `WebSearch` for market sizing data. Execute 3-5 targeted searches:
  - "[market category] market size [current year]"
  - "[market category] TAM [analyst firm]" (HolonIQ, Gartner, Grand View Research, Mordor Intelligence)
  - "[specific segment] spending [geography]"
  - "education assessment technology market growth"
  - "[specific theme] edtech market opportunity"
- Use `WebFetch` to extract specific data points from promising search results
- Capture every data point with source URL and publication date
- Flag any source older than 2 years

**Output of this step:** A filter chain showing broadest market → each successive filter (with source) → TAM → SAM → SOM.

### Step 4: Bottom-Up Estimation

Build an estimate from buyer-level economics.

**Methodology:**

1. Identify target buyer type:
   - K-12: School districts (US: ~13,000), individual schools (~130,000)
   - Higher ed: Institutions (US: ~4,000 degree-granting), departments within institutions
   - Both: State education agencies (50), international ministries of education
2. Count buyers using public data:
   - NCES (National Center for Education Statistics) for US institution counts
   - State department of education data for district counts
   - International equivalents where applicable
3. Estimate spend per buyer:
   - Use comparable product pricing where available (your organization's pricing, competitor pricing)
   - EdTech procurement benchmarks (per-student spend, per-institution spend)
   - Government education technology budgets
4. Multiply: buyer count x spend per buyer = bottom-up TAM
5. Apply SAM and SOM filters consistent with top-down methodology

**Search strategy:**

- "[buyer type] count [geography] [year]" (NCES, government data)
- "[product category] pricing per student" or "per institution"
- "education technology spending per student [segment]"
- "[competitor] pricing" for benchmark data
- ESSER/Title I/federal education technology funding data for K-12

**Output of this step:** A build-up showing buyer count x spend per buyer = estimate, with SAM/SOM applied.

### Step 5: Reconciliation

Compare top-down and bottom-up results and produce a final estimate range.

**Reconciliation protocol:**

1. Compare TAM estimates from both methodologies
2. If within 2x of each other: methodologies converge — present the range as the estimate band
3. If >2x divergence: investigate why
   - Common causes: different market definitions, inclusion/exclusion of adjacent categories, geographic scope mismatch, outdated data in one methodology
   - Adjust the methodology with the identified issue and re-estimate
   - If divergence persists after adjustment, present both with explanation of why they differ
4. Present conservative / moderate / aggressive estimates:
   - **Conservative:** Lower of the two methodologies, lower-bound assumptions
   - **Moderate:** Midpoint with balanced assumptions
   - **Aggressive:** Upper of the two methodologies, optimistic assumptions
5. SOM cap: Apply your SOM cap rules based on your organization's actual market position per segment.

**Sensitivity analysis:**

- Identify the 2-3 highest-impact variables (e.g., addressable institution count, spend per student, geographic scope)
- Show +/- 25% range impact on TAM for each variable
- This tells the reader which assumptions matter most

### Step 6: Write Research Artifact

**Ad-hoc mode:** Skip this step — there is no idea to relate an artifact to. Jump to Step 7 with findings going to the database and conversation only.

**Idea mode:**

1. Get today's date using `Bash(date:*)`: `date +%Y-%m-%d` (the local date)
2. Create the artifact as a new row in the Research database with one `notion-create-pages` call (`allow_async` false, so the row's URL comes back). A row of this type may already exist for the idea from a prior run: do not look for it and do not change it. Every run creates a new row dated today, and earlier rows stay.
3. Row parent: the Research data source — the `collection://` URL passed as `research_data_source=` when a caller gave one; otherwise fetch the `notion_research` database and take the data source it lists.
4. Row fields (these replace the artifact file's front matter), then the body structure:

| Field | Value |
| --- | --- |
| `Name` | `TAM Estimate: {Idea Title}` |
| `Idea` | a one-item array holding the idea row's URL |
| `Research type` | `tam-estimate` |
| `date:Created:start` | today, `YYYY-MM-DD` (with `date:Created:is_datetime` 0) |
| `Confidence` | `high`, `medium` or `low` |

Never write a value outside a field's options. If Notion refuses the create because a field lacks the option, report which option is missing and present the estimate in the output; do not create the row under another value.

**Run under `/thesis-test`.** When the caller's execution contract names another Research type and Name for the artifact row (`/thesis-test` does: `thesis-test-lens`, `thesis-test-{lens}-{date} ({slug})`) and a verdict record for its body, create the row with those in place of the type, Name and body template here. Parent, `Idea`, `Created` and the rest are unchanged.

The row body (the artifact; its title is the row's Name and is not repeated):

```markdown
**Idea:** {the idea's slug}
**Date:** {today's date}
**Confidence:** {High/Medium/Low}

## Market Definition

[Precisely what market is being sized. In scope / out of scope.]

## TAM / SAM / SOM

| Level | Conservative | Moderate | Aggressive | Methodology | Confidence |
|-------|-------------|----------|------------|-------------|------------|
| TAM | $X | $X | $X | [Key assumptions] | High/Med/Low |
| SAM | $X | $X | $X | [Filters applied] | High/Med/Low |
| SOM | $X | $X | $X | [Capture rationale] | High/Med/Low |

## Top-Down Analysis

### Broadest Market
[Starting point with source.]

### Filter Chain
| Filter | Value | Resulting Market | Source |
|--------|-------|-----------------|--------|
| [Geography] | [%] | $X | [Source, date] |
| [Segment] | [%] | $X | [Source, date] |
| [Category] | [%] | $X | [Source, date] |
| [Buyer type] | [%] | $X | [Source, date] |

### Top-Down Result
- TAM: $X
- SAM: $X
- SOM: $X

## Bottom-Up Analysis

### Buyer Identification
[Target buyer type and rationale.]

### Buyer Count
| Segment | Count | Source |
|---------|-------|--------|
| [e.g., US K-12 districts] | [N] | [Source, date] |
| [e.g., US higher ed institutions] | [N] | [Source, date] |

### Spend Per Buyer
[Estimation methodology with benchmarks and sources.]

### Bottom-Up Result
- TAM: $X (buyer count x spend per buyer)
- SAM: $X
- SOM: $X

## Reconciliation

**Divergence:** [Within 2x / >2x — explanation]
**Resolution:** [How divergence was resolved or explained]

## Key Assumptions

| Assumption | Supporting Evidence | Sensitivity Impact |
|------------|--------------------|--------------------|
| [Assumption 1] | [Evidence + source] | [High/Med/Low — what happens if wrong] |
| [Assumption 2] | [Evidence + source] | [High/Med/Low] |
| [Assumption 3] | [Evidence + source] | [High/Med/Low] |

## Sensitivity Analysis

| Variable | Base Case | -25% Impact | +25% Impact |
|----------|-----------|-------------|-------------|
| [Variable 1] | $X | $X | $X |
| [Variable 2] | $X | $X | $X |
| [Variable 3] | $X | $X | $X |

## Sources

| # | Source | Date | Data Point | Notes |
|---|--------|------|------------|-------|
| 1 | [Source name + URL] | [Date] | [What was cited] | [Flag if >2 years old] |
| 2 | ... | ... | ... | ... |

## Limitations

[What could not be validated. What data gaps exist. No fabrication — state clearly what is estimated vs. sourced.]

## Revenue-Potential Connection

[How this TAM analysis feeds into the idea's revenue-potential impact dimension. What rating (Low/Med/High) this evidence supports and why.]
```

1. The idea's research list is its `Research` relation, and setting `Idea` on the new row is what adds the artifact to it. Make no write to the idea row.
   - Do not remove or change earlier rows of this type from prior runs — they coexist
   - Do NOT modify any field of the idea row or its body content
   - Keep the URL the create returned: it is the artifact reference Step 7 reports

### Step 7: Present Results

Present the completed TAM estimate to the user with:

```text
TAM estimation complete: {idea-name}

**Market definition:** [One sentence]

**TAM / SAM / SOM (Moderate estimates):**
| Level | Estimate | Confidence |
|-------|----------|------------|
| TAM | $X | High/Med/Low |
| SAM | $X | High/Med/Low |
| SOM | $X | High/Med/Low |

**Methodology:** Top-down and bottom-up reconciled. [Convergence/divergence note.]

**Key assumptions:**
- [Assumption 1]
- [Assumption 2]
- [Assumption 3]

**Limitations:**
- [Key limitation 1]
- [Key limitation 2]

**Revenue-potential implication:** This evidence supports a [Low/Med/High] rating for the revenue-potential impact dimension because [one sentence rationale].

**Research artifact written to:** {URL of the artifact row}
**Idea research list updated:** the Research relation now includes the tam-estimate row.
```

Your impact-dimension signals are advisory. If a signal contradicts the idea card's existing ratings (the row's impact-dimension fields), state the contradiction explicitly in your report — do not silently align to the card. The same applies to factual claims: if your research contradicts a factual claim in the card body, surface the contradiction prominently in your final report — not buried in the artifact — so the orchestrator can reconcile the card.

After presenting the above, review your findings against the shared research capture heuristic: **Sourced + Durable + Decision-relevant + Shared** (applies to TAM figures, growth rates, buyer counts, and market benchmarks that would benefit other ideas). Write qualifying findings to the strategy research database:

```bash
python3 scripts/research-db.py write-findings --json '{
  "findings": [
    {
      "claim": "...",
      "evidence": "...",
      "confidence": "high|medium|low",
      "source_url": "https://specific-page-url (REQUIRED — not a homepage)",
      "source_description": "fallback only when no stable URL exists",
      "ttl_months": 24,
      "topic": "market-sizing",
      "category": "tam-broad|tam-segment|growth-rate",
      "capabilities": ["slug-1", "slug-2"],
      "competitor_id": null
    }
  ]
}'
```

**Source URL requirement:** Every finding MUST have a `source_url` with the most specific available page — not a homepage. Use `source_description` only when no stable URL exists, with enough detail to locate the source. Do not write findings with neither.

## Stop Rules

At any point during execution, stop and report when:

| Condition | Action |
| ----------- | -------- |
| Idea too abstract to define market scope | Stop. Report: "Cannot define a market to size. The idea needs more specificity on what problem it solves, for whom, and through what mechanism." Ask human to refine. |
| No reliable market data after 5+ searches | Present what was found with Low confidence flags on all estimates. Write the artifact row with "Insufficient Data" markers. Do not fabricate numbers. |
| Market scope requires internal revenue data | Stop. Note that external-only sources are insufficient for this specific estimate. Ask human to provide internal data or adjust scope. |
| Idea serves a market completely outside education | Stop. Flag as out-of-domain for this estimation framework. |

## Error Handling Summary

| Condition | Behavior |
| ----------- | ---------- |
| No argument and no ideas exist | Report "No ideas found in the Ideas database" and exit |
| Idea not found | Fuzzy match or report with available slugs, exit |
| Idea mode with a pointer missing | Report which pointer is missing and that `--adhoc` needs none, exit |
| Idea row cannot be read | Report the issue with specifics, exit |
| `Domain` field empty | Report "Idea missing `Domain` field — needed to scope market definition." Ask human to add it, exit |
| Market too broad to size meaningfully | Ask human to narrow the scope, exit |
| No market data available across all searches | Write artifact with "Insufficient Data" flags, Low confidence on all estimates |
| Artifact row creation fails | Report error, present the estimate in the output so the work is not lost, exit |
| The created row does not show the idea in its `Idea` relation | Report error — the artifact row was still written; give its URL and ask human to set the relation by hand |

## Scope Boundaries

This skill does NOT:

- Change the idea's stage
- Modify the idea body content
- Create or modify the idea row; its only trace on the idea is the new artifact row in the `Research` relation
