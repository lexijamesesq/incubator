---
name: develop
description: This skill should be used when the user asks to "develop an idea", "develop [idea name]", "work on [idea name]", or "move [idea] to developing". Transforms a seed-stage idea into a researched TL;DR nugget (Stage 1→2) by researching strategic context, market intelligence, and related ideas, then delegating strategic synthesis to the develop-synthesis agent.
argument-hint: [idea-name]
context: conversation
disable-model-invocation: false
allowed-tools:
  - Read
  - Edit
  - Write
  - Glob
  - Grep
  - WebSearch
  - WebFetch
  - Bash(date:*)
  - Bash(python3 scripts/research-db.py:*)
  - Bash(mkdir:*)
  - mcp__obsidian__read_note
  - mcp__obsidian__read_multiple_notes
  - mcp__obsidian__write_note
  - mcp__obsidian__patch_note
  - mcp__obsidian__update_frontmatter
  - mcp__obsidian__search_notes
  - mcp__obsidian__list_directory
  - mcp__obsidian__get_frontmatter
  - Skill
  - Agent
---

# /develop — Seed Development Session (Stage 1→2)

Transforms a seed-stage idea into a researched, assessed TL;DR nugget. Researches strategic context, market intelligence, and related ideas, then delegates strategic synthesis to the develop-synthesis agent running in an isolated context optimized for judgment-heavy work.

## Invocation

```text
/develop [idea-name]
```

- Required argument: the name of a seed-stage idea file in `Ideas/`
- If no argument provided: list available seed-stage ideas and ask the user to pick
- Examples: `/develop foraging-intelligence`, `/develop cache-optimization`

## Arguments

Parse `$ARGUMENTS` to resolve the target idea file.

**Resolution rules:**

| Input | Behavior |
| ------- | ---------- |
| Empty | List all seed-stage ideas in Ideas/, ask user to select |
| `idea-name` | Resolve to `Ideas/{idea-name}.md` |
| `idea-name.md` | Strip `.md`, resolve as above |
| `--format strategy-doc\|product-brief` | Optional flag — sets the Step 9 verdict format rec and skips the format-recommendation prompt |

**Fuzzy matching:** If exact match fails, list all `.md` files in Ideas/ and find filenames containing the argument as a substring (case-insensitive). If exactly one match, use it. If multiple matches, present options and ask user to pick. If zero matches, report and exit.

## Role

You are the orchestrator for the /develop pipeline. You handle research, human interaction, and coordination. Strategic synthesis is delegated to the develop-synthesis agent, which runs in an isolated context with a clean window optimized for judgment-heavy work.

You are working on behalf of the role specified in CLAUDE.md (Configuration > Role). Your output serves two audiences:

- **Internal:** The user uses TL;DR nuggets to prioritize which ideas to develop further
- **External:** TL;DR nuggets may be pushed to JPD for stakeholder visibility via /jpd-push

## Reference Material

`incubator-reference.md` is a thin section index. Load only the `reference/` section files this skill needs — not the whole set:

- `reference/stage-model.md` — Stage 1→2 transition semantics
- `reference/frontmatter-schema.md` — card frontmatter, impact dimensions, theme governance
- `reference/templates.md` — TL;DR Template (the card this skill produces) and Seed Template
- `reference/architecture.md` — Step 3 cross-stage detection, consolidation, merge mechanics
- `reference/research-protocol.md` — research streams, cross-domain discovery, when to pause and ask
- `reference/shared-research.md` — Snowflake query/write, capture heuristic, TTL reference
- `reference/voice-and-output-standards.md` — the "Designers speaking Design" exit test for Stage 2 output

## Execution Flow

Execute these steps in order. Stop and report errors at any step rather than continuing with bad data.

### Step 0: Parse Arguments

1. Read `$ARGUMENTS`. Also parse an optional `--format strategy-doc|product-brief` flag — record it for the Step 9 verdict format rec.
2. If empty: use `Glob` to list all `.md` files in `Ideas/`. Read each file until the first `###` heading or 40 lines (whichever comes first) to check frontmatter for `stage: seed`. Present seed-stage ideas to the user and ask them to select one. If no seed-stage ideas exist, report "No seed-stage ideas found in Ideas/" and exit.
3. If provided: attempt to resolve `Ideas/{argument}.md`
   - Try exact match first (with and without `.md` extension)
   - If not found, try fuzzy substring match against all filenames in Ideas/
   - If exactly one fuzzy match, use it
   - If multiple fuzzy matches, present options and ask user to pick
   - If zero matches, report "Idea file not found: {argument}. Available files in Ideas/: {list}" and exit

### Step 0.5: Pre-Flight

Before the ~8-minute research spend, verify the ground:

- **cwd is project root:** `ls scripts/research-db.py`. If absent, halt: "Run /develop from the Incubator project root."
- **research-db reachable:** run `python3 scripts/research-db.py lookup-capabilities --json '{}'` (this is also Step 1's baseline probe). On failure, emit the reauth/cd fix from the Error Handling table and halt before fan-out.
- **MCP state:** if Atlassian MCP is disconnected, tell the human NOW that /cross-domain (Step 4 Stream C) is skipped unless they reconnect. In-session auth has required a full session exit-and-resume to clear — surface that rather than burn the spend first.

### Step 1: Load Context

Load these files in parallel:

1. **Seed file** at the resolved path — full content
2. **Persona guide** — `persona.md`
3. **OKRs** — Read the OKRs document (path configured in CLAUDE.md under Configuration > External References > `strategic_context.okrs`)
4. **Idea index** — Use `Glob` to list all `.md` files in `Ideas/`, then apply tiered reading:
   - **Complete-stage ideas:** Read frontmatter only (first 25 lines or until `---` closes). Extract: stage, themes, domain. These provide theme vocabulary only — complete ideas are excluded from Step 3 matching.
   - **All other ideas (seed, developing, drafting, refining):** Read until first `###` heading or 40 lines. Extract: frontmatter + header fields (Core insight, Problem, Who cares, Strategic connection). Used by Step 3 to verify refine-seed's related-ideas resolution AND portfolio context in the synthesis handoff.
   From the loaded index, extract all unique `themes` values across all idea files into a **portfolio theme vocabulary** — the canonical set of themes in use. Used in Step 5e to ensure theme reuse.
5. **Shared research baseline** — Query the strategy research database for structured competitive intelligence, customer evidence, and market sizing relevant to this idea's capabilities:

   ```bash
   python3 scripts/research-db.py lookup-capabilities --json '{}'
   python3 scripts/research-db.py query-landscape --json '{"capabilities": ["slug-1", "slug-2"]}'
   python3 scripts/research-db.py query-gaps --json '{"capabilities": ["slug-1", "slug-2"]}'
   ```

   Derive capability slugs from the seed's `themes` and `core insight` using the vocabulary list — themes may map directly or expand (e.g., `ai-capabilities` → `ai-item-generation`, `ai-open-response-scoring`). Entries within TTL are baseline; entries past TTL are directional only and require reverification during Stream A/B research. Gap detection identifies where enrichment agents should focus live web research.

6. **Competitor registry** — Snowflake `competitors` table. Already covered by item 5 above's `query-landscape` call (returns name, category, market_tier, pricing_model, matched capabilities filtered by the seed's capability slugs). For competitors central to the seed's competitive frame, follow up with `query-competitor` for the full intelligence body and linked findings.

### Step 2: Validate the Seed

Confirm the seed file has:

- `stage: seed` in frontmatter
- Core insight populated in body (non-empty)
- Source populated in body (non-empty)
- Initial strategic connection populated in body (non-empty)
- `domain` set in frontmatter
- `themes` with at least one entry in frontmatter

**If any required field is missing:** Report exactly which fields are missing and exit. Do not proceed with incomplete seeds.

**If `stage` is not `seed`:** Report "Idea '{name}' is at stage '{current-stage}', not 'seed'. This skill only develops seed-stage ideas." and exit.

### Step 3: Verify Seed Refinement

**Prerequisite:** Seeds should be refined via `/refine-seed` before development. Refinement handles intent clarification (capability-absent vs. experience-broken), header field drafting, related ideas matching, and merge/keep decisions.

Check the seed file for refinement indicators:

- **Core insight** populated (non-empty, one sentence)
- **Initial strategic connection** populated (names a priority and mechanism)
- **related-ideas** frontmatter resolved (may be empty if no relations exist — that's valid)

**If header fields are missing or empty:** Report: "Seed '{name}' appears unrefined — Core insight and/or Strategic connection missing. Run `/refine-seed {name}` first to clarify intent and position in the portfolio, then re-run /develop." Exit.

**If header fields are present:** Proceed. The seed has been through intent refinement and is ready for research.

### Step 4: Research

Conduct five research streams. Streams B-E invoke specialized agents; Stream A is orchestrator-executed and splits across two phases — its internal-context half (Phase 1b) runs concurrently with the agent fan-out, its shared-research half (Phase 3) after the database refresh. Prioritize depth over breadth — 3 strong findings beat 10 shallow ones.

#### Phase 1: Agent Research (parallel fan-out)

Launch FOUR research agents — divergent-thinking, educator-sme, edtech-sme, tam-estimate — as parallel background subagents in a SINGLE message via the Agent tool: one `Agent` call per stream, all in the same message, with `subagent_type` set to the matching agent name. They run concurrently in isolated contexts; no agent depends on another's output. Each produces a research artifact at `Research/{idea-name}/` and returns its held-back writes-of-record as payloads for the orchestrator to apply in Phase 1.5.

**Status ping:** immediately post one line to the human — "4 research streams launched (divergent, educator, edtech, tam), ~5–8 min in background; next human touchpoint is Step 9." Post a second one-liner when synthesis returns (Step 5).

- **`divergent-thinking`** (Stream E: Divergent Discovery) — structural analogies and "the disruptive one." Reads ONLY the idea file; no web or DB access, so it is the fastest stream. Produces `Research/{idea-name}/divergent-angles.md`.
- **`educator-sme`** (Stream D: Educator Perspective) — adoption realism, pain point validity, classroom barriers, skeptic/champion scenarios. Produces `Research/{idea-name}/educator-evaluation.md`.
- **`edtech-sme`** (Stream B: Market Intelligence — Competitive) — positioning, market fit, technology risk, go-to-market, strategic timing. Produces `Research/{idea-name}/edtech-market-analysis.md`.
- **`tam-estimate`** (Stream B: Market Intelligence — Sizing) — TAM/SAM/SOM with top-down/bottom-up reconciliation and sensitivity analysis. Produces `Research/{idea-name}/tam-estimate.md`.

Each subagent's SKILL.md assumes slash-command invocation — a parsed `$ARGUMENTS`, a cwd-relative `research-db.py`, generic file tools. None of that holds under a pointer-invoked Agent call, so the prompt supplies the argument explicitly and overrides those assumptions with an execution contract. Use this pointer-prompt template per agent, substituting `{idea-name}` and `{skill}` (the agent's skill directory name, e.g. `educator-sme`):

```text
Read your operational protocol at claude/skills/{skill}/SKILL.md (via Obsidian MCP read_note if generic Read is redirected) and execute it in idea-mode for the idea: {idea-name}.
Execution contract (overrides where the protocol assumes slash-command invocation):
- Treat {idea-name} as the parsed argument; you are in idea-mode.
- Write your research artifact to Research/{idea-name}/ exactly per your protocol's artifact template (Obsidian MCP write_note for .md files).
- HOLD BACK writes-of-record: do NOT run research-db.py write commands (write-findings, upsert-competitor) and do NOT modify the idea card or its frontmatter. Return these as exact executable payloads in your final report (full command JSON; the research-array entry) for the orchestrator to apply.
- research-db.py READ queries (lookup-*, query-*) are allowed; run them from the project root.
- Bound your web research: 3-6 targeted searches; stop when your artifact template's fields are covered.
- Final report: artifact path written, held-back payloads verbatim, advisory impact-dimension signals, any blocker encountered.
```

**divergent-thinking variant:** divergent-thinking does no web research and no DB access by design, so omit the two contract lines about research-db.py READ queries and bounded web research. It still holds back frontmatter writes — its HOLD BACK line reduces to "do NOT modify the idea card or its frontmatter; return your research-array entry in your final report for the orchestrator to apply."

**Model overrides:**

| Agent | Model |
| ------- | ------- |
| edtech-sme | Sonnet-class |
| tam-estimate | Sonnet-class |
| educator-sme | Sonnet-class |
| divergent-thinking | session model |

Overrides are persona-rubric-gated; a lens that fails its rubric reverts to session model. Gate records: `Eval/Suites/enrichment-skills/Runs/`.

**/cross-domain (Stream C) — immediately after the parallel block:** Invoke `/cross-domain {idea-name}` via the Skill tool exactly as before — it overlaps the background agents. It queries JPD for ideas from other product domains with functional overlap, classifies signals as Direct overlap, Enabler/dependency, or Convergence, and writes `Research/{idea-name}/cross-domain-signals.md`. Its existing behavior, output handling, and Step 5b are unchanged.

**Agent failure handling:** The four streams run concurrently, so evaluate their reports as a set once they return rather than one at a time. A failure in any one stream (timeout, stop rule, error, or no report) does not affect the others and no single agent blocks the pipeline — record the failed or empty stream by name with its reason in Phase 1.5 and continue with the successful streams. See the error handling table for per-agent fallback behavior.

##### Phase 1b: Stream A part 1 — Internal Strategic Context (orchestrator, concurrent with the fan-out)

No agent covers this — strategy docs, NPS, and OKRs require internal file access. **Start it as soon as the four agents are launched and run it while they are in flight.** It reads internal vault files only and depends on nothing the agents produce or write, so holding it until after the fan-out leaves the orchestrator idle across the entire research window for no gain. It must finish before Phase 1.5 begins.

Stream A's remaining half — the shared-research reconciliation — genuinely depends on Phase 1.5's writes and the Phase 2 refresh, and stays where it is as Phase 3. Do not pull it forward.

- Grep the product strategy document (path configured in CLAUDE.md under Configuration > External References > `strategic_context.product_strategy`) for the seed's theme keywords and domain terms. Extract relevant passages. Never load the full file.
- Scan the seed file's `### Original Capture` section for strategic signals, connections, or context that didn't make it into the seed's structured fields. Raw captures often contain intuitive connections and half-formed insights that inform research direction.
- Grep the design strategy document (path configured in CLAUDE.md under Configuration > External References > `strategic_context.design_strategy`) for relevant design priorities.
- Reference the OKRs loaded in Step 1 — identify which 2026 goals this idea would advance.
- **NPS customer signal check (two-pass):** For the relevant product(s), scan NPS analysis files in the directories configured under `metrics.nps_product_a` and `metrics.nps_product_b`. Cap the scan to files from the past 12 months.

  **Pass 1 — Longitudinal keyword scan (all months within 12-month window):**
  Derive 3-5 search terms from the seed's themes, core insight, and domain terms. Grep ALL `.md` files in each NPS directory for those terms. Record which files (months) contain matches and which do not. If zero files match across all months for a product, record: "Zero mentions of {topic} across {N} months of {product} NPS data ({date range})" — this distinguishes latent demand (observable in behavior, not voiced in feedback) from articulated demand, and directly informs the Customer Sentiment dimension.

  **Pass 2 — Targeted section reads:**
  - **Always:** Read the **Top Pain Points** and **The Signal** sections from the **3 most recent** files per product (6 files total). These sections are small (~10-16 lines each) — use the Read tool with offset/limit to target them directly rather than grepping then conditionally reading.
  - **If Pass 1 matched older files:** Also read **Top Pain Points**, **The Signal**, and **3 Things That Matter** from each matched file for verbatim quotes and trend context.
  - Do not read Summary, What's Working, or Document Links sections. Do not read raw CSV data or full analysis files.

  NPS findings directly inform the Customer Sentiment dimension rating. Absence of signal across the full window is itself evidence — note it explicitly in the handoff.

###### Phase 1.5: Serialized writes-of-record

**Resume after interruption/restart:** list `Research/{idea-name}/` first — a stream whose artifact file exists is complete (its held-back payload is in its report if recoverable, else re-derivable from the artifact); relaunch ONLY missing streams. After applying writes-of-record, immediately create `Research/{idea-name}/development-research.md` as a one-line stub "Phase 1.5 writes-of-record applied {date}" (Step 8 expands it). This stub is the duplicate-write guard: if it exists, do NOT re-apply DB writes.

**Wait for completion first:** Before beginning Phase 1.5, the orchestrator must wait for all four background agents' completion reports and the /cross-domain return. Proceed on partial results only per the stream-failure rules in item 3 below.

The parallel agents held back every write-of-record; the orchestrator applies them serially here, after all four agents report and /cross-domain returns. Serialization is deliberate — concurrent writes to the shared card frontmatter and to the research database must not happen in-stream.

1. **Validate and apply database payloads.** For each held-back `research-db.py` write payload (`write-findings`, `upsert-competitor`), validate before executing: capability slugs resolve via `lookup-capabilities`, `source_url` is present, and the `claim` is a substantive assertion (not a search query, bare citation, or bookmark). Execute the passing write commands one at a time from the project root. A payload that fails validation is surfaced to the human with the specific failure reason — never silently dropped.
2. **Append artifact paths in one write.** Collect ALL new artifact paths returned by the successful agents and append them to the idea card's `research:` frontmatter array in a SINGLE read-modify-write operation: read the current array, append the new paths, and write once via `update_frontmatter`. Do not issue per-agent frontmatter writes — the agents held these back precisely so the orchestrator serializes them.
3. **Record stream outcomes.** A stream that failed or returned no report is recorded by name with its failure reason; continue with the successful streams. The existing per-agent failure rules (error handling table) apply, and Phase 4's EdTech WebSearch fallback is unchanged.

###### Phase 2: Refresh Shared Research Baseline

After Phase 1.5 applies the held-back writes, re-query the research database to pick up the findings and competitor entries just written:

- `python3 scripts/research-db.py query-landscape --json '{"capabilities": ["slug-1", "slug-2"]}'` — refreshed findings + competitor metadata

Phase 1.5 applied `upsert-competitor` for new/updated competitors and `write-findings` for new findings from the agents' held-back payloads. This refresh ensures Phase 3 works from the latest state.

###### Phase 3: Stream A part 2 — Shared-Research Reconciliation (orchestrator)

Stream A's internal-context half already ran during the fan-out (Phase 1b). What remains is the part that genuinely depends on Phase 1.5's applied writes and the Phase 2 refresh — it cannot move earlier.

- **Shared research check:** Review the refreshed database query results for findings relevant to this idea's problem space. Note which entries are within TTL (usable as baseline) versus past TTL (directional only — reverify). This now includes any findings applied in Phase 1.5 from the agents' held-back payloads.
- For each finding, note connection strength: **direct** (explicitly named), **adjacent** (related priority, plausible mechanism), or **indirect** (thematic only).
- **Database enrichment:** When specific competitors surface during Stream A research, use the database for targeted deep-dives:

  ```bash
  python3 scripts/research-db.py query-competitor --json '{"name": "Competitor Name"}'
  ```

  This retrieves the full profile (intelligence body, all findings, capability tags) for that specific competitor — richer context than the local file frontmatter alone. Use selectively for competitors that are central to the idea's competitive positioning, not for every competitor in the registry.

###### Phase 4: Stream B Fallback (orchestrator — only if edtech-sme failed)

If `/edtech-sme` failed in Phase 1, execute fallback market intelligence research:

- Use `WebSearch` for competitor landscape, market trends, technology enablers, and customer signals.
- Execute 3-5 targeted searches derived from the seed's themes and core insight.
- Capture findings with source URLs.
- Target: named competitors, specific capabilities, technology shifts.

This preserves current Stream B quality when the agent is unavailable. If edtech-sme succeeded, skip this phase entirely — the agent's output is the market intelligence.

###### Phase 5: Read Agent Artifacts

Read all successfully produced agent artifacts to prepare for handoff creation:

- `Research/{idea-name}/edtech-market-analysis.md` (if edtech-sme succeeded)
- `Research/{idea-name}/tam-estimate.md` (if tam-estimate succeeded)
- `Research/{idea-name}/educator-evaluation.md` (if educator-sme succeeded)
- `Research/{idea-name}/divergent-angles.md` (if divergent-thinking succeeded)
- `Research/{idea-name}/cross-domain-signals.md` (if cross-domain succeeded)

Extract key findings from each for the handoff. For agent artifacts, preserve specificity — copy key sections verbatim (competitor tables, TAM summary tables, adoption assessments) rather than summarizing. The synthesis agent depends on this specificity.

**Exception: cross-domain.** The synthesis agent does not use cross-domain data — it goes directly to the card as a post-synthesis section (Step 5b). Include only the status line (succeeded/failed + signal count) in the handoff, not the full signal list.

### Step 4.5: Create Synthesis Handoff

After all research phases complete, create the handoff artifact at `Research/{idea-name}/synthesis-handoff.md`. Create the directory if it does not exist.

This artifact is the curated research input for the synthesis agent. Preserve specific data points, named capabilities, URLs, issue keys, and connection strengths — the synthesis agent depends on this specificity. For agent-produced sections, extract key sections verbatim from the artifacts rather than summarizing. For shared research entries, include the specific URL from each entry's `Source:` field — the synthesis agent uses these URLs for Research Summary citations and cannot guess them.

```markdown
# Research Handoff: {idea-name}

**Date:** {today}
**Idea:** {title from seed}
**Seed core insight:** {from seed body}
**Seed strategic connection:** {from seed body}

---

## Strategic Context (Stream A)

### Product Strategy — {connection strength}
- {Finding with connection strength noted}
- {Finding with connection strength noted}

### Design Strategy — {connection strength}
- {Finding with specific design priority named}

### OKR Connections
- {OKR reference}: {how this idea advances it}

### NPS / Customer Evidence
- {Product} ({date range}): {key finding or "Zero mentions of {topic}"} ([{Product} NPS — {Month YYYY} tab]({external_url from CLAUDE.md > Configuration > metrics.nps_product_a or .nps_product_b}))
- **Key finding:** {synthesis of NPS evidence or absence}

Citation rule: each NPS bullet must end with a linked source pointing at the configured Google Doc URL for the product (`external_url` field under the matching `metrics.nps_product_*` config key in CLAUDE.md > Configuration > External References). Use the tab name (e.g., "March 2026 tab") in the link text so the reader knows which tab to navigate to. Local file paths under the configured `path` value MUST NOT appear in citations — they're internal scan locations, not viewable sources.

### Shared Research Baseline (within TTL)
- {Finding} ({confidence level}) ([Source Title](specific URL from entry's Source: field))
- {Finding} ({confidence level}) ([Source Title](specific URL from entry's Source: field))

---

## Market Intelligence (Stream B — EdTech SME)

{If edtech-sme succeeded: extract verbatim from edtech-market-analysis.md}
{If edtech-sme failed: populate from fallback web searches using the format below}

### Market Fit: {Strong/Moderate/Weak}
{One-sentence verdict + 2-4 sentences of supporting analysis}

### Competitive Positioning
| Competitor | Relevant Capability | Comparison |
|------------|---------------------|------------|
| {Name} | {What they do} | {Differentiation / Parity / Behind} |

Tag each competitor as `(registry)` or `(discovered)` to distinguish registry-sourced from organically-discovered competitors. This traceability supports eval criteria and registry maintenance.

**Positioning narrative:** {2-3 sentences}

### Technology Risk: {Low/Medium/High}
{2-3 sentences on maturity, integration requirements, build/buy considerations}

### Strategic Timing
{2-3 sentences on market window, urgency signals}

{If edtech-sme failed, note: "Market intelligence from fallback web searches — EdTech SME unavailable: {reason}"}

---

## Market Sizing (Stream B — TAM Estimate)

{If tam-estimate succeeded: extract from tam-estimate.md}
{If tam-estimate failed: note absence}

### TAM / SAM / SOM
| Level | Moderate Estimate | Confidence |
|-------|-------------------|------------|
| TAM | ${X} | {High/Med/Low} |
| SAM | ${X} | {High/Med/Low} |
| SOM | ${X} | {High/Med/Low} |

### Key Assumptions
- {Assumption 1 with sensitivity impact}
- {Assumption 2 with sensitivity impact}

### Revenue-Potential Signal: {Low/Med/High}
{One sentence connecting TAM to the idea's revenue path}

{If tam-estimate failed: "Market sizing unavailable — {reason}. Revenue-potential dimension lacks quantitative evidence."}

---

## Educator Perspective (Stream D)

{If educator-sme succeeded: extract from educator-evaluation.md}
{If educator-sme failed: note absence}

### Adoption Assessment: {High/Medium/Low}
{One-sentence verdict}

### Pain Point Validity
{2-3 sentences on problem reality from educator daily experience}

### Adoption Barriers
{Specific friction points — concrete workflow realities}

### Champion Scenario
{One concrete scenario: role, context, what happens, outcome}

{If educator-sme failed: "Educator perspective unavailable — {reason}. Customer-sentiment and user-experience dimensions rely on NPS and shared research only."}

---

## Cross-Domain Discovery (Stream C)
{Succeeded — {N} signals | Failed — {reason}}

---

## Divergent Reframing (Stream E)

{If divergent-thinking succeeded: include the disruptive angle as a reframing candidate}
{If divergent-thinking failed: omit this section}

### The Disruptive Angle: {title}
{The connection — 2-3 sentences from the divergent-angles.md artifact}
{What it opens up — 1-2 sentences}

*This is a reframing candidate, not evidence. The synthesis agent decides whether it strengthens the strategic compound.*

---

## Research Synthesis

**Strategic connection:** {Strong/Medium/Weak}. {1-2 sentence summary of why.}

**Market validation:** {Strong/Medium/Weak}. {1-2 sentence summary. Reference edtech-sme market fit when available.}

**Customer evidence:** {Strong/Medium/Weak}. {1-2 sentence summary. Note latent vs. articulated demand. Reference educator-sme adoption assessment when available.}

**Competitive gap:** {Confirmed/Partial/Unconfirmed}. {1-2 sentence description. Reference edtech-sme competitive positioning when available.}

**Revenue signal:** {Strong/Medium/Weak}. {1-2 sentence summary. Reference tam-estimate when available.}

---

## Portfolio Context

### Related Ideas (header fields for differentiation)

{For each related idea resolved during /refine-seed (verified in Step 3):}

**{idea-name}** ({stage})
- Core insight: {from their card}
- Problem: {from their card}
- Who cares: {from their card}
- Strategic connection: {from their card}
```

Populate from Step 4 research findings. Sections with no findings should note the absence explicitly (e.g., "Zero mentions of {topic} in NPS data" or "Cross-domain discovery unavailable — MCP timeout"). Agent sections that failed should include the failure note per the template above.

### Step 4.6: Handoff Fidelity Check (skeptic)

Always runs. Launch the `skeptic` agent (Agent tool, fresh context) in handoff-fidelity mode: it reads the lens artifacts and `synthesis-handoff.md` and reports whether curation dropped counter-signals, softened hedges or confidence levels, or lost artifact-self-flagged warnings ("candidate, not evidence"; "do not average"; break-condition-grade objections). Fix the handoff per its findings — or override a finding with a stated reason — BEFORE invoking synthesis. The curator cannot audit its own compression.

### Step 5: Strategic Synthesis

Invoke the synthesis agent to produce the TL;DR card content.

**Spine snapshot (before invoking synthesis):** record three things from the seed as it exists right now — (1) the exact text of its `Initial strategic connection` line, (2) every interrogative sentence in its `### Original Capture` section, and (3) any non-null impact-dimension ratings in frontmatter. Write them as a `## Spine Snapshot` section appended to the END of `synthesis-handoff.md` (connection line verbatim; interrogative sentences; non-null ratings) — Step 9's spine check reads it from there, never from memory. The synthesis overwrites the card; this snapshot is the only diff source against seed state. Skip the snapshot (and the Step 9 spine check) when the Original Capture is under ~80 words — a seed that thin has no spine to rubber-stamp.

**Invoke via Skill tool:**
Use the Skill tool with skill name `develop-synthesis`, passing the idea name as the argument.

The develop-synthesis skill declares `context: fork`, so it executes in an isolated forked context with a clean window. It reads the seed file, the synthesis handoff (created in Step 4.5), the persona guide, the format example, and related ideas context. It produces the completed TL;DR card — frontmatter updates (stage, dimensions) and body content (header fields, opportunity assessment, research summary, thought outline, open questions).

After the agent returns, read the updated idea file to confirm synthesis completed (stage changed to `developing`, impact dimensions populated).

If the agent reports insufficient research or a stop condition, surface it to the user and halt.

### Step 5b: Cross-Domain Signals Section

If /cross-domain succeeded, write a `### Cross-Domain Signals` section to the card after the Research Summary section. The content comes from the /cross-domain skill's Phase 3 formatted output (already in the orchestrator's context from the /cross-domain Skill-tool invocation during Phase 1) — transfer it directly, no reformatting needed (Phase 3 output uses the card section format).

If the Phase 3 output is no longer in context, re-read the artifact at `Research/{idea-name}/cross-domain-signals.md` and apply the same curation the skill applies in Phase 3: include convergence group members, direct overlap items, and enablers that are specifically load-bearing for this idea's core capability. Maximum 5 signals. Write using the card section format:

```markdown
### Cross-Domain Signals
{N} ideas from other domains with possible functional overlap:
- [{issue-key}]({url}) {summary} ({Domain Label}) — {Signal type}: {Connection sentence}
```

Issue keys are linked using the Atlassian base URL from the artifact. Include convergence group descriptions after the signal list only when they add insight beyond what the individual entries state — a cross-cutting pattern or strategic implication that emerges from the combination.

If /cross-domain failed, omit the section entirely.

### Step 5c: Buildable Surface Check

After synthesis completes, invoke the buildable surface enrichment agent to check whether the Thought Outline is principle-shaped or feature-shaped.

**Invoke via Skill tool:**
Use the Skill tool with skill name `buildable-surface`, passing the idea name as the argument (e.g., `foraging-intelligence`).

The buildable-surface skill declares `context: fork`, so it executes in an isolated forked context. It reads the idea card and research artifacts, applies a three-signal detection heuristic, and either:

- **No-ops** (feature-shaped) — no section added, proceed to Step 6
- **Fires** (principle-shaped or borderline) — writes a `### Buildable Surface` section between Thought Outline and Open Questions

Either way, proceed to Step 5d. If the skill reports an error (e.g., research too thin for grounded candidates), note it in the Step 9 presentation and proceed.

### Step 5d: Disruptive Reframing Section

If `/divergent-thinking` succeeded, write a `### Disruptive Reframing` section to the card between Thought Outline and Buildable Surface (or between Thought Outline and Open Questions if Buildable Surface did not fire). The content is a 2-3 sentence distillation of the disruptive angle from `Research/{idea-name}/divergent-angles.md`.

Read the artifact and locate "## The Disruptive One" — the divergent-thinking skill identifies one of its 3-5 angles as the disruptive frame. Distill from that angle's "The connection" and "What it opens up" content. Stay close to the artifact's language; do not generatively rewrite. Use the format:

```markdown
### Disruptive Reframing
**{Disruptive Angle Title}** — {2-3 sentence insight summarizing the connection and what it opens up}
```

This section is card-canonical — `/jpd-push` Step 3b reads it from the card first, with self-heal fallback to the artifact if missing. The card content must match exactly what gets pushed to JPD; do not add additional paragraphs, links, or commentary that would not also appear in JPD.

If `/divergent-thinking` failed or no `divergent-angles.md` exists, omit the section entirely.

### Step 5e: Theme Management

Using the portfolio theme vocabulary collected in Step 1 and the research findings from Step 4, assess whether the seed's theme classifications still hold.

**General theme assessment:**

- For each existing theme: does research confirm this idea is substantively about this theme, or was it a surface-signal classification? Remove if incidental.
- For themes in the portfolio vocabulary NOT on the seed: did research reveal a genuine connection the router missed? Add if substantive. Only use existing themes — never invent new ones.
- Minimum one theme per idea.

**ai-capabilities special case:**

Does AI make or break this idea?

- **Requires AI** → add the tag. The feature doesn't work without it.
- **Enhanced by AI** → add the tag. Works without AI, but AI is a natural progressive enhancement — not forced.
- **AI would be forced** → don't add. Solution looking for a problem.

Check the research before deciding — cross-domain signals, buildable surface candidates, and competitive landscape show what the market assumes about the mechanism. For cross-domain signals, re-read the artifact at `Research/{idea-name}/cross-domain-signals.md` if the Phase 1 output is no longer in context — the synthesis handoff does not carry cross-domain detail.

**Record all changes** (additions/removals with one-sentence rationale each) for Step 9 presentation.

### Step 5f: Title Revision

Assessment question: "If someone reads only this title and the Core insight sentence, do they get an accurate picture of what this idea is?"

**Revise when:** research shifted the idea's center of gravity, the router title reflects raw capture framing rather than developed understanding, or the title is too generic to distinguish from other portfolio ideas.

**Keep when:** title is still accurate and specific after research.

**Constraint:** Filename stays stable — it's the identifier across related-ideas, research folders, and jira-key. Only the `## [Heading]` in the body changes.

**Record** before/after for Step 9 presentation.

### Step 6: Critic Review

After writing the card to file, invoke the artifact critic to check structural and voice conformance. This runs in a forked, isolated context to avoid same-pass confirmation bias.

**Invoke via Skill tool:**
Use the Skill tool with skill name `artifact-critic`, passing the completed idea card file path as the argument (e.g., `Ideas/foraging-intelligence.md`).

The artifact-critic skill declares `context: fork`, so it runs in an isolated forked context — separate from this session — with read access to vault notes via Obsidian MCP. It returns a deviation report.

**Triage the findings:**
For each finding the critic returns, either:

- **Fix it** in the idea file, or
- **Override it** with a stated reason (the deviation is intentional and improves the artifact)

If any findings are overridden, note them in the Step 9 presentation under the confidence assessment so the human has visibility.

**Critic-skipped fallback:**
If the artifact-critic invocation returns an error, fails to produce a deviation report, or otherwise does not complete its check, do NOT silently proceed. The orchestrator must:

1. Note the failure reason in working memory.
2. Perform a best-effort self-review against the format spec and persona guide as a stopgap.
3. Explicitly surface in Step 9 under the confidence assessment: "Artifact-critic skipped — {reason}. Self-review only; independent adversarial check did not run."

The point of this skill is the independent check. A silent skip turns synthesis self-evaluation into the only quality gate, which is exactly the bias the critic exists to backstop. The human should always know whether the critic actually ran.

### Step 7: Self-Critique

After addressing critic findings, check the completed TL;DR against these criteria that require the full research context. Fix issues directly in the file:

1. **Multiplicative framing:** Does the Thought Outline show compounding value across dimensions? One move unlocking value in multiple directions simultaneously.
2. **Specificity:** Is the language precise? Names and mechanisms over abstractions. Specificity in the card means *precise language*, not *inline data* — N-values, survey sizes, and market figures belong in the research artifact.
3. **Strategic realism:** Are connections honest? Use "supports" not "advances" for indirect connections. Do not overstate alignment.
4. **Business language:** Would a VP understand without translation? No design methodology language.
5. **Completeness:** Every section has real content. No placeholders except Open Questions (which should have genuine unknowns).

Fix all issues directly in the file before proceeding.

**Human review awareness:** After presentation, the human evaluates using the Stage 2→3 review template (`Templates/review-templates.md`). That template focuses on: core framing accuracy, impact dimension credibility, strategic connection reality, output format readiness, and blocking unknowns. Anticipate these checks — if you know a dimension is shaky, say so in your confidence assessment rather than letting the human discover it.

### Step 8: Create Research Artifact and Verify Frontmatter

The synthesis handoff was created in Step 4.5. This step creates the full persistent research artifact and verifies all research paths are in frontmatter.

1. Create directory `Research/{idea-name}/` if it does not exist
2. Write `Research/{idea-name}/development-research.md` containing:
   - Search queries executed (both Grep patterns and WebSearch queries from Stream A and any fallback)
   - Agent invocation results (which succeeded, which failed, failure reasons)
   - Raw findings with sources (URLs, file paths)
   - Synthesis notes connecting findings to the idea
   - Date of research
   Both files persist — `synthesis-handoff.md` is the curated input to the synthesis agent, `development-research.md` is the full research trail for downstream stages.
3. **Frontmatter verification:** Read the idea file's `research:` array. Phase 1.5 appended each successful agent's artifact path (the agents hold back frontmatter writes so the orchestrator can serialize them in one read-modify-write). Verify all expected paths are present and add any that are missing:
   - `Research/{idea-name}/synthesis-handoff.md` (orchestrator — always)
   - `Research/{idea-name}/development-research.md` (orchestrator — always)
   - `Research/{idea-name}/edtech-market-analysis.md` (if edtech-sme succeeded)
   - `Research/{idea-name}/tam-estimate.md` (if tam-estimate succeeded)
   - `Research/{idea-name}/educator-evaluation.md` (if educator-sme succeeded)
   - `Research/{idea-name}/divergent-angles.md` (if divergent-thinking succeeded)
   - `Research/{idea-name}/cross-domain-signals.md` (if cross-domain succeeded)

### Step 9: Present for Review

Lead with the verdict block; then details. Do NOT dump the full card inline — link it, show on request.

```text
{idea} → developed · confidence: {level} · spine: {moved|unchanged|skipped-thin} · format rec: {strategy-doc|product-brief}
credibility: {clean | amber ({n}): {signals}}
next: accept · press harder (targeted re-run) · /thesis-test (≈half a develop) · /draft · revise
```

- **confidence:** High (strong connection + market validation + clear impact path) / Medium (gaps in market data or impact clarity) / Low (weak connections, thin research, open questions).
- **spine:** from the spine check below. **format rec:** the `--format` value if supplied (Step 0), else the recommendation derived below.
- **credibility token — computed mechanically.** `clean` unless any fire → `amber ({n}): {named signals}`: spine diff unchanged-and-rubber-stamp-suspect (when run), any lens fell back or failed, thin research array, zero genuine Open Questions on a complex idea, flat rating variance. Thin-seed branch (spine check skipped): token uses confidence + lens count only. Name any unresolved Step 4.6 skeptic flags here.

**Research summary:**

- Stream A (Internal): {N} connections ({direct/adjacent/indirect})
- Stream B (EdTech SME): {market fit {verdict}, {N} competitors | fallback web searches}
- Stream B (TAM): {TAM ${X}, confidence {level} | unavailable}
- Stream C (Cross-domain): {N signals | unavailable — {reason}}
- Stream D (Educator): {adoption {verdict} | failed — {reason}}
- Stream E (Divergent): {disruptive angle: {title} | failed — {reason}}

**Related seeds:** {list or "none found"}

**Classification updates:**

- Title: {unchanged | "Old" → "New"}
- Themes: {unchanged | added: [x], removed: [z] — rationale per change}
- AI Feature (JPD): {Yes — load-bearing | No — value stands without AI}

**Spine check (rubber-stamp detector):** {Skipped — seed too thin | results below}. Read the `## Spine Snapshot` section from `synthesis-handoff.md` — never from memory:

- Strategic connection: {moved — seed text replaced | UNCHANGED from seed}
- Seed capture questions: {N of M survive in Open Questions}
- Seed dimension ratings: {n/a — seed had none | {K} of {J} unchanged}
- Mechanical rule: string-level diff (normalized whitespace, substring survival) — never a judgment call.
{If strategic connection UNCHANGED **and** half or more seed questions survive: "The developed card preserved the seed's strategic spine — research may have confirmed it, or no agent challenged it. A `/thesis-test {idea-name}` tests the spine adversarially while keeping this run's artifacts." Weight self-filter: this offer matters for gnarly, net-new, or critical tradeoffs in positioning or approach — a spine-preserved feature card inside an existing strategic direction can read it and move on. Otherwise omit — when the spine moved, say only what moved, one line.}

**Output format recommendation** (omit if `--format` was supplied): **strategy-doc** (positioning play, narrative framing, multi-product direction, capability shaping how products evolve) or **product-brief** (scoped initiative with features, JTBD, timeline, defined deliverable). State which signals the idea exhibits. The human decides; the skill does NOT set `output-file`.

**Full card:** `Ideas/{idea-name}.md` — shown on request, not dumped inline.

**Database write-back:**

After presenting the TL;DR, review all findings from this development session against the shared research capture heuristic (Sourced + Durable + Decision-relevant + Shared). Write qualifying findings to the strategy research database so future runs benefit from structured, queryable intelligence:

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
      "topic": "competitive-landscape|customer-evidence|market-sizing|enrichment",
      "category": "capability-specific|capability-presence|competitive-gap|...",
      "capabilities": ["slug-1", "slug-2"],
      "competitor_id": "uuid-or-null"
    }
  ]
}'
```

**Source URL requirement:** Every finding written to the database MUST have a `source_url` with the most specific available page (press release, feature page, research report) — not a homepage. If no stable URL exists, use `source_description` with enough detail to locate the source (publication name, date, title). Do not write findings with neither. This is the same standard applied to shared research file entries.

Use `python3 scripts/research-db.py lookup-competitor --json '{"name": "..."}'` to resolve competitor names to IDs. Prioritize findings that close gaps identified in Step 1 database queries.

**Competitor registry updates:**

Update via `upsert-competitor` (Snowflake-backed). See the edtech-sme skill for the full command schema. Summary:

- **New competitors:** Run `upsert-competitor` with full fields + evidence (`source_url` required). Fuzzy dup check returns candidates if a similar name exists — review and either pass `force_create: true` (new entity) or update the matched row instead.
- **Existing competitors:** Same command. Exact-name lookup hits the existing row; `last_researched` stamps automatically.
- **Category changes:** The command returns `action: needs_category_confirmation` rather than auto-applying. Surface the proposal to the human. Never pass `force_category_change: true` from a skill — that flag is human-only.
- **Found-superseded:** If the command returns `action: found_superseded`, surface to the human; never auto-revive.

Note in the presentation:
> **Competitor registry updated:**
>
> - New: {list with category and capabilities, or "none"}
> - Updated: {list with what changed, or "none"}
> - Category changes proposed: {list with rationale, or "none"}
> - Superseded entries surfaced: {list with name, or "none"}

## Stop Rules

At any point during execution, stop and report when:

| Condition | Action |
| ----------- | -------- |
| Core insight already addressed by existing initiatives | Stop. Report what you found. Classify as "redirect" if initiative is in a different domain, "duplicate" if same domain. |
| No strategic connection can be established honestly | Stop. Report: no connection found after searching strategy docs and OKRs. Classify as "pause" (no foundation). |
| Critical context can only come from human | Stop. Report what's missing and why you cannot research it. Ask the human to provide. |
| Idea too vague to research meaningfully | Stop. Report: core insight too abstract for targeted research. Ask human to sharpen it. |
| Idea serves a domain outside the configured project domain (see CLAUDE.md > Configuration > Role) | Stop. Flag for rerouting to appropriate domain leader. Classify as "redirect". |
| Self-declared weakness in strategic connection | Treat as pre-filter signal. Validate quickly (one targeted Grep + one OKR check) before investing in full research. If validation fails, fire stop rule. |

**Minimum strategic connection threshold:** A viable connection requires at least one of:

- (a) Direct reference in product or design strategy docs
- (b) Direct advancement of a named 2026 OKR
- (c) Two or more adjacent connections to named priorities with a plausible mechanism

If none exist, the stop rule fires. When stopping, distinguish between:

- **Redirect:** Idea has merit but belongs in a different domain
- **Pause:** Idea lacks strategic foundation entirely

When stopping, state explicitly: what was found, what is missing, and what would unblock further development.

## Error Handling Summary

| Condition | Behavior |
| ----------- | ---------- |
| No argument and no seed-stage ideas exist | Report "No seed-stage ideas found in Ideas/" and exit |
| Idea file not found | Report with available filenames from Ideas/ listing, exit |
| Idea not at seed stage | Report current stage, exit |
| Missing required frontmatter fields | Report specific missing fields, exit |
| Missing required body sections (core insight, source, strategic connection) | Report specific missing sections, exit |
| Strategy doc Grep returns no results | Note "No matches found in {doc}" as a finding, continue to next stream |
| `/edtech-sme` fails (any reason) | Orchestrator falls back to 3-5 web searches for competitive landscape (current Stream B behavior). Note in handoff: "Market intelligence from fallback web searches — EdTech SME unavailable: {reason}." |
| `/tam-estimate` fails (any reason) | Note in handoff: "Market sizing unavailable — {reason}. Revenue-potential dimension lacks quantitative evidence." Continue. |
| `/educator-sme` fails (any reason) | Note in handoff: "Educator perspective unavailable — {reason}." Customer-sentiment and user-experience rely on NPS and shared research only. Continue. |
| `/divergent-thinking` fails (any reason) | Omit Divergent Reframing section from handoff. Continue. |
| `/cross-domain` fails (MCP auth/timeout) | Note "Cross-domain discovery unavailable — {reason}" in handoff. Continue. |
| All research streams empty (zero findings across all streams) | Fire stop rule — no strategic foundation. Report and exit. |
| Seed file has malformed frontmatter | Report parsing issue with specifics, exit |
| Related seed has malformed frontmatter | Log under "Index Issues", continue matching other seeds |
| Synthesis agent reports insufficient research | Surface the agent's assessment to the user, halt |
| Synthesis handoff creation fails | Report the error and halt |
| research-db.py fails at Step 0.5/1 | Surface the auth/cwd fix (reauth, or cd to project root); halt before fan-out |
| Single stream needs backfill later | Re-run just that lens via its pointer-prompt; then follow the /thesis-test Step 6 pattern — append results to synthesis-handoff.md, re-invoke develop-synthesis |

## Scope Boundaries

This skill does NOT:

- Perform strategic synthesis — that is the develop-synthesis agent's job
- Refine seeds, clarify intent, or resolve related ideas — that is `/refine-seed`'s job (run it first)
- Create seed files (that is the router's job via `/process-inbox`)
- Decide output format — strategy doc vs. product brief (that is a human decision at Stage 2→3)
- Draft the full document (that is the `/draft` skill, Stage 2→3)
- Run the Sufficiency Evaluator (planned MLP-phase agent — not yet built)
- Process inbox items (that is `/process-inbox`)
- Merge or consolidate ideas (that is `/refine-seed`'s job)
- Load full strategy docs into context (Grep only — paths configured in CLAUDE.md under Configuration > External References > `strategic_context.product_strategy` and `strategic_context.design_strategy`)
- Invoke Gemini CLI (notes Atlassian references for manual lookup instead)
- Modify the idea file body after Stage 2 — the idea card is the permanent scannable artifact. /develop enriches it (Stage 1→2); subsequent stages create linked output documents.
