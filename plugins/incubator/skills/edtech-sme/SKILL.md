---
name: edtech-sme
description: This skill should be used when the user asks to "get market analysis for [idea]", "edtech evaluation of [idea/subject]", "competitive analysis for [idea/subject]", "market perspective on [company/technology/concept]", or "edtech SME review of [subject]". Evaluates a strategic idea OR an arbitrary subject (competitor, technology, concept) against edtech market dynamics, competitive landscape, buyer behavior, and technology trends from an industry analyst perspective.
argument-hint: [idea-name]
context: fork
agent: edtech-sme
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

# /edtech-sme — EdTech Market Analysis (Enrichment Agent)

Evaluates a strategic idea against edtech market dynamics, competitive landscape, buyer behavior, and technology trends. Produces a research artifact from an outside-in industry analyst perspective. This is an enrichment agent — it does NOT change the idea's stage.

## Invocation

```text
/edtech-sme [idea-name]                  # idea mode
/edtech-sme --adhoc "subject string"     # ad-hoc mode
```

Two modes:

- **Idea mode** (naked argument): the argument names an idea file in `Ideas/`. Skill loads the idea and evaluates it. Writes a local artifact at `Research/{idea-name}/edtech-market-analysis.md` and appends the path to the idea's `research: []` frontmatter.
- **Ad-hoc mode** (`--adhoc "subject"`): the flag carries a free-form subject string (competitor, technology, concept). Skill evaluates the subject on its own. No local artifact, no frontmatter update. Findings still write back to the research database.

Examples: `/edtech-sme foraging-intelligence`, `/edtech-sme --adhoc "Top Hat"`, `/edtech-sme --adhoc "adaptive learning platforms"`.

## Arguments

Parse `$ARGUMENTS` to determine mode:

- If `--adhoc "subject"` present: **ad-hoc mode**, subject = value of flag. Skip Ideas/ resolution entirely.
- Otherwise: **idea mode**, naked argument = candidate idea name.

**Idea-mode resolution (fail-closed):**

| Input | Behavior |
| ------- | ---------- |
| Empty | Glob `Ideas/*.md`, present titles, ask user to select |
| `idea-name` or `idea-name.md` | Exact match at `Ideas/{arg}.md` (strip `.md` first) |
| No exact match | Case-insensitive substring match against all `Ideas/*.md` filenames |
| Single fuzzy match | Use it |
| Multiple fuzzy matches | Present options, ask user to pick |
| Zero matches | **ERROR** (see below) — never silently fall through to ad-hoc |

**Zero-match error text:**

> Idea file not found: `{arg}`. Closest candidates in Ideas/: `{list up to 5 filenames with lowest edit distance or shortest substring proximity}`. For ad-hoc analysis of a non-idea subject, use: `/edtech-sme --adhoc "{arg}"`.

Exit. Do NOT silently interpret a no-match as ad-hoc mode.

## Persona

This skill runs in the edtech-sme agent's context. The agent carries the full industry analyst persona, domain knowledge (competitors, buyer dynamics, dual-role entities), evaluation framework, and quality standards. See `.claude/agents/edtech-sme.md`.

**Invocation note:** When executed by a pointer-invoked agent rather than the Skill tool: generic Read/Write/Edit on vault .md files may be redirected — use the Obsidian MCP equivalents; run research-db.py from the project root.

**Output serves two purposes:**

- **Enrichment:** Feeds into the idea's `industry-disruption`, `revenue-potential`, and `strategic-alignment` impact dimension assessments
- **Research artifact:** Preserved at `Research/[idea-name]/edtech-market-analysis.md` for reference during drafting and refining stages

## Execution Flow

Execute these steps in order. Stop and report errors at any step rather than continuing with bad data.

### Step 0: Parse Arguments

1. Read `$ARGUMENTS`. Detect `--adhoc` flag.
2. **If `--adhoc "subject"` is present:** mode = `ad-hoc`, subject = value of flag. Skip Ideas/ resolution. Proceed to Step 1.
3. **Otherwise (idea mode):**
   - If empty: use `Glob` to list all `.md` files in `Ideas/`. Present all ideas to the user (with their stage from frontmatter) and ask them to select one. If no ideas exist, report "No ideas found in Ideas/" and exit.
   - Try exact match at `Ideas/{argument}.md` (strip `.md` extension first if present)
   - If no exact match, try case-insensitive substring match against all filenames in `Ideas/`
   - Single fuzzy match → use it
   - Multiple fuzzy matches → present options, ask user to pick
   - Zero matches → **ERROR**: "Idea file not found: `{argument}`. Closest candidates in Ideas/: `{list up to 5}`. For ad-hoc analysis of a non-idea subject, use: `/edtech-sme --adhoc \"{argument}\"`." Exit. Do NOT silently interpret as ad-hoc.

### Step 1: Load Context

**Idea mode:** Read the idea file at the resolved path — full content including frontmatter and body. Extract:

- **Core insight** — the central idea being evaluated
- **Themes** — from frontmatter `themes: []` array
- **Domain** — from frontmatter `domain:` field
- **Stage** — from frontmatter `stage:` field (for reporting, not gating)
- **Existing research** — from frontmatter `research: []` array (to avoid duplicating work)

**Ad-hoc mode:** The subject string is the target. There is no idea file, no themes, no domain, no prior research. Frame the evaluation around the subject itself — the company, technology, or concept — rather than an idea being evaluated against the market.

**Shared research baseline:**

- **Idea mode:** Query by capability slugs derived from the idea's `themes` field:

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

**Cross-idea awareness:** If your competitive research reveals that the same competitor landscape applies to another idea you've seen in the Ideas/ directory (from the argument resolution step), note it in the artifact: "Competitive overlap: similar landscape applies to [other-idea-name]." This is informational only — do not modify the other idea's files.

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

**Ad-hoc mode:** Skip this step entirely — no idea-scoped folder to write to, no frontmatter to update. Jump to Step 7 (present results) with findings going to the database and conversation only.

**Idea mode:**

1. Get today's date using `Bash(date:*)`: `date +%Y-%m-%d`
2. Create directory `Research/{idea-name}/` if it does not exist (use `Bash` to `mkdir -p`)
3. Write the research artifact to `Research/{idea-name}/edtech-market-analysis.md` (if a file already exists at this path from a prior run, write to `Research/{idea-name}/edtech-market-analysis-{YYYY-MM-DD}.md` instead; if that also exists, append `-2`, `-3`, etc., for same-day collisions)

**Artifact structure:**

```markdown
---
type: incubator/research
agent: edtech-sme
idea: {idea-name}
created: {YYYY-MM-DD}
confidence: high | medium | low
---

# EdTech Market Analysis: {Idea Title}

**Idea:** {Core insight from idea file}
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

1. Update the idea file frontmatter: append the written artifact path to the `research: []` array

   **Frontmatter update rules:**
   - Read the current frontmatter to get the existing `research:` array
   - Append the new path to the array (do not overwrite existing entries, do not remove older dated-suffix entries from prior runs)
   - Do NOT change any other frontmatter fields (especially `stage:`)
   - Use `Edit` to make the targeted frontmatter change

### Step 7: Present Results

**Idea mode:** Present the completed analysis with the idea-name, impact dimension implications (for /develop synthesis), and the research artifact path.

**Ad-hoc mode:** Present the analysis with the subject string, omit impact dimension implications entirely, omit research artifact path. Findings still go to the database.

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

**Research artifact:** Research/{idea-name}/edtech-market-analysis.md
**Confidence:** {High/Medium/Low}
```

Your impact-dimension signals are advisory. If a signal contradicts the idea card's existing frontmatter ratings, state the contradiction explicitly in your report — do not silently align to the card. The same applies to factual claims: if your research contradicts a factual claim in the card body, surface the contradiction prominently in your final report — not buried in the artifact — so the orchestrator can reconcile the card.

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
| No argument and no ideas exist | Report "No ideas found in Ideas/" and exit |
| Idea file not found | Fuzzy match against available filenames. If no match, report with available filenames and exit |
| Idea too abstract for market lens | Report what is missing (product concept, buyer persona, competitive frame) and ask human for refinement. Exit. |
| No competitive data available | Write artifact with low confidence flags on all dimensions. Note data limitations explicitly in each section. |
| WebSearch returns no results for a query | Note the failed query, try alternative search angle. If all searches fail, proceed with low confidence. |
| Research directory creation fails | Report error with specifics, exit |
| Frontmatter update fails | Report error, note the research artifact was written successfully and the frontmatter path needs manual addition. Exit. |

## Scope Boundaries

This skill does NOT:

- Change the idea's stage (enrichment only)
- Modify the idea body content (only appends to `research:` frontmatter array)
- Recommend go/no-go decisions (that is a human decision)
