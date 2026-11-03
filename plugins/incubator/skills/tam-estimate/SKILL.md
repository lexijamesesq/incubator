---
name: tam-estimate
description: This skill should be used when the user asks to "estimate TAM for [idea]", "size the market for [idea/subject]", "market sizing for [idea/subject]", "TAM analysis for [idea]", or "TAM estimate for [market category]". Produces defensible TAM/SAM/SOM estimates using top-down and bottom-up methodologies for a strategic idea OR an arbitrary market category/segment in the assessment/edtech space.
argument-hint: [idea-name]
context: fork
agent: tam-estimate
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

# /tam-estimate — TAM Estimation Enrichment Agent

Produces defensible TAM/SAM/SOM estimates for a strategic idea in the assessment/edtech space. Uses top-down and bottom-up methodologies, reconciles divergence, and writes a research artifact. This is an enrichment agent — it does not change the idea's stage.

## Invocation

```text
/tam-estimate [idea-name]                  # idea mode
/tam-estimate --adhoc "market category"    # ad-hoc mode
```

Two modes:

- **Idea mode** (naked argument): sizes the market for an idea. Writes local artifact + updates idea frontmatter.
- **Ad-hoc mode** (`--adhoc "subject"`): sizes a free-form market category/segment. No local artifact, no frontmatter update. Findings still write back to the research database.

Examples: `/tam-estimate foraging-intelligence`, `/tam-estimate --adhoc "AI grading tools"`, `/tam-estimate --adhoc "K-12 authentic assessment"`.

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
| Zero matches | **ERROR**: "Idea file not found: `{arg}`. Closest candidates in Ideas/: `{list up to 5}`. For ad-hoc market sizing, use: `/tam-estimate --adhoc \"{arg}\"`." Exit. Do NOT silently fall through to ad-hoc. |

## Persona

This skill runs in the tam-estimate agent's context. The agent carries the full market sizing analyst persona, domain knowledge (products, segments, geography, business model), SOM cap rules, divergent analyst mode, and quality standards. See `.claude/agents/tam-estimate.md`.

**Invocation note:** When executed by a pointer-invoked agent rather than the Skill tool: generic Read/Write/Edit on vault .md files may be redirected — use the Obsidian MCP equivalents; run research-db.py from the project root.

Output feeds into the `revenue-potential` impact dimension and supports investment prioritization conversations with VPs and ELT.

## Execution Flow

Execute these steps in order. Stop and report errors at any step rather than continuing with bad data.

### Step 0: Parse Arguments

1. Read `$ARGUMENTS`. Detect `--adhoc` flag.
2. **If `--adhoc "subject"` is present:** mode = `ad-hoc`, subject = value of flag. Skip Ideas/ resolution. Proceed to Step 1.
3. **Otherwise (idea mode):**
   - If empty: `Glob` `Ideas/*.md`, read first 20 lines of each for frontmatter (stage, domain, themes), present all ideas with stage, ask user to select. If none exist, exit.
   - Try exact match at `Ideas/{argument}.md` (strip `.md` first)
   - If no exact match, case-insensitive substring match
   - Single fuzzy match → use it
   - Multiple fuzzy matches → present options, ask user to pick
   - Zero matches → **ERROR**: "Idea file not found: `{argument}`. Closest candidates in Ideas/: `{list up to 5}`. For ad-hoc market sizing, use: `/tam-estimate --adhoc \"{argument}\"`." Exit. Do NOT silently fall through to ad-hoc.

### Step 1: Load Context

**Idea mode:** Load the idea file at the resolved path — full content (frontmatter + body). Extract:

- `domain` — assessments, platform, or cross-product
- `themes` — thematic keywords for search targeting
- **Core insight** — from body content
- **Problem it addresses** — from body content (if populated; may not exist at seed stage)

**Ad-hoc mode:** The subject string is the market category to size. No idea file, no themes, no domain. Frame Step 2 market scope entirely from the subject string. Ad-hoc subjects are expected to be reasonably specific (e.g., "K-12 authentic assessment" not "edtech"); if the subject is too broad, Step 2's stop rule fires.

**Shared research baseline:** Query the strategy research database for TAM figures, growth rates, and buyer benchmarks:

```bash
python3 scripts/research-db.py query-landscape --json '{"capabilities": ["cap-slug-1", "cap-slug-2"]}'
```

Derive capability slugs from the idea's `themes` field. Within-TTL entries are known starting points — do not re-research established sizing data that is already documented and current. Past-TTL entries are directional only (useful for market category framing, not current figures).

No other files needed. TAM estimation is externally validated — internal strategy docs are not relevant.

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

**Ad-hoc mode:** Skip this step — no idea-scoped folder, no frontmatter to update. Jump to Step 7 with findings going to the database and conversation only.

**Idea mode:**

1. Get today's date using `Bash(date:*)`: `date +%Y-%m-%d`
2. Write `Research/{idea-name}/tam-estimate.md` using the Write tool (which auto-creates intermediate directories). If a file already exists at that path from a prior run, write to `Research/{idea-name}/tam-estimate-{YYYY-MM-DD}.md` instead; if that also exists, append `-2`, `-3`, etc., for same-day collisions. Structure:

```markdown
---
type: incubator/research
research-type: tam-estimate
idea: {idea-name}
created: {today's date}
confidence: high | medium | low
---
# TAM Estimate: {Idea Title}

**Idea:** {idea-name}
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

1. Update the idea file frontmatter: append the written artifact path to the `research: []` array.
   - Read the idea file
   - Find the `research:` line in frontmatter
   - If `research: []` (empty array), replace with `research:\n  - {written path}`
   - If `research:` already has entries, append the written path after the last entry
   - Do NOT remove older dated-suffix entries from prior runs — augment artifacts coexist
   - Do NOT modify any other frontmatter fields or body content

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

**Research artifact written to:** Research/{idea-name}/tam-estimate.md
**Idea frontmatter updated:** research array now includes tam-estimate path.
```

Your impact-dimension signals are advisory. If a signal contradicts the idea card's existing frontmatter ratings, state the contradiction explicitly in your report — do not silently align to the card. The same applies to factual claims: if your research contradicts a factual claim in the card body, surface the contradiction prominently in your final report — not buried in the artifact — so the orchestrator can reconcile the card.

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
| No reliable market data after 5+ searches | Present what was found with Low confidence flags on all estimates. Write the artifact with "Insufficient Data" markers. Do not fabricate numbers. |
| Market scope requires internal revenue data | Stop. Note that external-only sources are insufficient for this specific estimate. Ask human to provide internal data or adjust scope. |
| Idea serves a market completely outside education | Stop. Flag as out-of-domain for this estimation framework. |

## Error Handling Summary

| Condition | Behavior |
| ----------- | ---------- |
| No argument and no ideas exist | Report "No ideas found in Ideas/" and exit |
| Idea file not found | Fuzzy match or report with available filenames, exit |
| Idea file has malformed frontmatter | Report parsing issue with specifics, exit |
| Missing domain in frontmatter | Report "Idea missing `domain` field — needed to scope market definition." Ask human to add it, exit |
| Market too broad to size meaningfully | Ask human to narrow the scope, exit |
| No market data available across all searches | Write artifact with "Insufficient Data" flags, Low confidence on all estimates |
| Research directory creation fails | Report error, exit |
| Frontmatter update fails | Report error — artifact was still written, ask human to manually add research path |

## Scope Boundaries

This skill does NOT:

- Change the idea's stage
- Modify the idea body content
- Create or modify the idea file beyond the `research:` frontmatter array
