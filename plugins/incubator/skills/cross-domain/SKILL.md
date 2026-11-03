---
name: cross-domain
description: This skill should be used when the user asks to "check cross-domain signals for [idea]", "cross-domain discovery for [idea/subject]", "what are other teams building related to [idea/subject]", "cross-domain [idea]", or "cross-domain signals for [capability/concept]". Queries the JPD project for ideas from other product domains that have functional overlap with an Incubator idea OR an arbitrary subject.
argument-hint: [idea-name]
context: fork
disable-model-invocation: false
allowed-tools:
  - Read
  - Glob
  - Bash(date:*)
  - Bash(mkdir:*)
  - mcp__atlassian__searchJiraIssuesUsingJql
  - mcp__obsidian__read_note
  - mcp__obsidian__write_note
  - mcp__obsidian__patch_note
  - mcp__obsidian__update_frontmatter
  - mcp__obsidian__list_directory
---

# /cross-domain — Cross-Domain JPD Discovery (Enrichment Agent)

Queries the JPD project for ideas from other product domains that have functional overlap with an Incubator idea. Surfaces what other teams are building (or have built) that intersects with the idea — a signal type no other part of the pipeline provides. This is an enrichment agent — it does NOT change the idea's stage.

**Precision over recall.** Returning "no cross-domain signals found" is a valid, confident result. Returning noise is unacceptable.

## Invocation

```text
/cross-domain [idea-name]                  # idea mode
/cross-domain --adhoc "subject string"     # ad-hoc mode
```

Two modes:

- **Idea mode** (naked argument): discovers cross-domain signals for an idea. Writes local artifact + updates idea frontmatter.
- **Ad-hoc mode** (`--adhoc "subject"`): discovers JPD items overlapping with a free-form subject (capability, concept). No local artifact, no frontmatter update.

Examples: `/cross-domain foraging-intelligence`, `/cross-domain --adhoc "rubric-based grading infrastructure"`.

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
| Zero matches | **ERROR**: "Idea file not found: `{arg}`. Closest candidates in Ideas/: `{list up to 5}`. For ad-hoc cross-domain discovery, use: `/cross-domain --adhoc \"{arg}\"`." Exit. Do NOT silently fall through to ad-hoc. |

## Role

You are a cross-domain discovery agent for the Strategy Incubator. Your job is to surface what other teams are building (or have built) in the JPD project that has functional overlap with an Incubator idea. You provide the internal organizational reality across product domains — a signal type that internal strategy docs (Stream A) and web research (Stream B) cannot provide.

You are precise and conservative. A confident "nothing found" is far more valuable than noisy matches. Every signal you surface must have a specific functional connection — not just thematic similarity.

**Who reads your output and what they do with it:** A product leader scans this section and decides whether they need to coordinate with another team. If the answer is yes, the issue keys tell them where to start. If the answer is no, they move on. They do not need an inventory of tangentially related work — they need the 3-5 signals that would change what they do next.

## Execution Flow

Execute these phases in order. Stop and report errors at any phase rather than continuing with bad data.

### Phase 0: Load Configuration

Read `jira-config.md` from the Incubator project root (`Projects/Incubator/jira-config.md`) via `mcp__obsidian__read_note`. All Jira connection details, field IDs, and JQL parameters used in this skill come from that file. Do not proceed if the file cannot be read.

### Phase 0.1: Parse Arguments

1. Read `$ARGUMENTS`. Detect `--adhoc` flag.
2. **If `--adhoc "subject"` is present:** mode = `ad-hoc`, subject = value of flag. Skip Ideas/ resolution. Proceed to Phase 0.5.
3. **Otherwise (idea mode):**
   - If empty: `Glob` `Ideas/*.md`, present all ideas with stage, ask user to select. If none exist, exit.
   - Try exact match at `Ideas/{argument}.md` (strip `.md` first)
   - If no exact match, case-insensitive substring match
   - Single fuzzy match → use it
   - Multiple fuzzy matches → present options, ask user to pick
   - Zero matches → **ERROR**: "Idea file not found: `{argument}`. Closest candidates in Ideas/: `{list up to 5}`. For ad-hoc cross-domain discovery, use: `/cross-domain --adhoc \"{argument}\"`." Exit. Do NOT silently fall through to ad-hoc.

### Phase 0.5: Load Context

Read the organizational structural reference: `.claude/skills/cross-domain/org-structural-reference.md`.

**Idea mode:** Also read the idea file at the resolved path — full content including frontmatter and body. Extract:

- **Core insight** — the central idea
- **Themes** — from frontmatter `themes: []`
- **Domain** — from frontmatter `domain:`
- **Original Capture** — raw context (often contains nuance the structured fields compressed)
- **Problem it addresses / Who cares** — if present (developing+ stage)
- **Strategic connection** — if present

**Ad-hoc mode:** The subject string is the anchor for overlap discovery. No idea file, no themes, no domain, no original capture. Subsequent phases use the subject string in place of the idea's extracted fields — Phase 1.5 Step B.1 extracts key terms directly from the subject string.

### Phase 1: Status-Partitioned Retrieve

Fetch all JPD ideas with structural metadata only (no descriptions). Use **status-partitioned queries** — one query per status — to avoid the 100-item-per-query ceiling that causes items to silently fall off the retrieval window.

**Why partitioned:** The MCP tool caps responses at 100 items and does not return pagination tokens. A single `ORDER BY updated DESC` query loses older-but-relevant items when the project exceeds 100 items. Status partitioning ensures active statuses (Experimentation, GTM, Opportunity Identification) — where the highest-value signals live — get complete coverage even as the project grows.

Run these 5 queries (sequentially — MCP calls cannot be parallelized):

```text
// Query 1: Active development (highest-value signals)
mcp__atlassian__searchJiraIssuesUsingJql(
    cloudId={Cloud ID from jira-config.md > Connection},
    jql='project = {project key} AND status = "2 - Experimentation" ORDER BY updated DESC',
    fields=["summary", "status",
            {Product Brand field ID}, {Product Domain field ID},
            {Squad field ID}, {Product Surface Area field ID},
            {Quarter Active field ID}],
    maxResults=100,
    responseContentFormat="markdown"
)

// Query 2: Shipping imminently
jql='project = {project key} AND status = "3 - GTM" ORDER BY updated DESC'

// Query 3: Planned/explored
jql='project = {project key} AND status = "1 - Opportunity Identification" ORDER BY updated DESC'

// Query 4: Already shipped (strongest signal weight — leverage or duplication)
jql='project = {project key} AND status = "Done" ORDER BY updated DESC'

// Query 5: Queued (weakest signal weight)
jql='project = {project key} AND status = "Backlog" ORDER BY updated DESC'
```

All queries use the same `fields` array and `maxResults=100`. Field IDs come from `jira-config.md > Static Field Values`.

**Merge results:** Combine all nodes into a single list. No deduplication needed — status partitions are mutually exclusive.

**Overflow detection:** If any individual query returns exactly 100 results, note it in the retrieval stats footer (e.g., "Done partition truncated at 100"). This is informational — the skill proceeds with what was retrieved. Active statuses (Experimentation, GTM, Opportunity Identification) are unlikely to overflow; Done and Backlog may.

**Error handling at this phase:**

- If MCP tools are unavailable or return auth error on the first query: surface the auth URL to the user, wait for the OAuth flow to complete, then retry the failed query once. If the retry succeeds, continue normally. If the retry also fails, stop and output: "Cross-domain discovery unavailable — Atlassian MCP authenticated but query still failed. Run `/mcp` to verify connection, then re-run." A retry that also fails has, in practice, required a full session exit-and-resume to clear — recommend that over further in-session retries.
- If MCP call times out on any query: Stop. Output: "Could not check — Atlassian MCP timed out. Cross-domain signals were not evaluated. Restart Claude Code to refresh connection."
- If ALL queries return 0 results combined: Stop. Output: "Warning: JPD queries returned 0 results across all statuses. This is unexpected — verify MCP connection. Cross-domain signals could not be evaluated."
- If some queries succeed and others fail: Continue with partial results. Note failed partitions in the retrieval stats footer.

Record total retrieved count across all queries.

### Phase 1.5: Structural Filter + Lightweight Relevance Scan

Two-step in-memory filter on Phase 1 results.

**Step A — Hard structural filter:**

- Exclude all results where Product Brand matches your own brand (value and field ID from `jira-config.md > Static Field Values` and `jira-config.md > Cross-Domain Query`). These are your team's ideas, not cross-domain.
- All other brands remain.

**Step B — Keyword auto-pass + LLM lightweight relevance scan:**

**B.1 — Extract key terms from the idea:**
From the idea's core insight, themes, domain, problem, who-cares, strategic connection, and original capture, extract a set of key terms — concept nouns, product names, capability words, and domain terms. Include both the specific terms (e.g., "Rubrics", "SpeedGrader", "grading") and their close variants. These are the terms that make a candidate worth looking at in Phase 2.

**B.2 — Keyword auto-pass:**
Any candidate whose summary contains one or more key terms (case-insensitive) passes automatically to Phase 2 without LLM judgment. This prevents the LLM from applying precision-level reasoning to candidates with obvious lexical overlap.

**B.3 — LLM scan on remaining candidates:**
For candidates that did NOT auto-pass, evaluate using the idea content (core insight, themes, domain, original capture, problem/who-cares/strategic-connection if available) and the organizational structural reference (squad descriptions, domain descriptions, surface area descriptions). Evaluate using **summary + structural metadata only** (brand, squad, domain, surface area, status): does this have plausible functional overlap with the idea?

This is a **recall-optimized** coarse filter — the bar is "plausible overlap," not "confirmed relevance." False positives are acceptable here (Phase 2 handles precision). False negatives are the risk. Enabler connections (infrastructure this idea could use) are often invisible from summaries alone — when a candidate's summary suggests adjacent capability even without direct overlap, keep it.

**When in doubt, keep.** Phase 2 fetches full descriptions and handles precision.

**Expected yield:** ~200-400 Phase 1 results (across all status partitions) -> ~120-250 after brand exclusion -> ~20-30 after relevance scan (keyword auto-pass + LLM scan combined).

Record counts at each stage for the retrieval stats footer.

### Phase 2: Full Relevance Judgment

Fetch full descriptions for Phase 1.5 survivors only:

```text
mcp__atlassian__searchJiraIssuesUsingJql(
    cloudId={Cloud ID from jira-config.md > Connection},
    jql='project = {project key from jira-config.md > Connection} AND key in ({surviving keys from Phase 1.5})',
    fields=["description"],
    maxResults=25,
    responseContentFormat="markdown"
)
```

If Phase 1.5 yields more than 25 survivors, batch into multiple queries of 25.

**Error handling:** If description fetch fails, fall back to summary + metadata only for relevance judgment (lower confidence). Add "(summary-only — description unavailable)" to affected signal lines.

**No description truncation.** Descriptions are fetched in full for the small survivor set.

**Relevance classification:** Classify each candidate as one of:

- **Direct overlap** — another team building the same capability (duplication risk, collaboration opportunity)
- **Enabler/dependency** — infrastructure this idea depends on or must coordinate with, where the human would need to engage with the other team or make a design decision based on the dependency. General platform improvements that benefit many ideas (responsive design, accessibility compliance, shipped foundational improvements) go into the artifact as reference context but are excluded from the Phase 3 output — unless the improvement is specifically load-bearing for THIS idea's core capability (e.g., rubric infrastructure improvements for a grading idea, content editor improvements for an authoring idea whose primary surface is the editor)
- **Convergence** — same user problem, different angle
- **Not relevant** — plausible structural match but no meaningful connection (silently dropped)

Only Direct overlap, Enabler, and Convergence results are surfaced.

**Convergence detection:** After classifying individual candidates, scan for convergence — multiple teams in different squads/brands addressing the same user need independently. A convergence group requires 2+ results from different squads/brands. Multiple items from the same squad sharing a theme are one team's roadmap, not convergence.

**Domain label derivation:** For each relevant signal, derive a domain label for reader orientation using this priority chain:

1. **Product Brand** (field ID from `jira-config.md > Static Field Values`) — if populated, use as domain label (e.g., "the LMS product", "the credentials product")
2. **Product Domain** (field ID from `jira-config.md > Static Field Values`) — if Brand is null but Domain is populated, use it (e.g., "Learning Management", "AI")
3. **Squad** (field ID from `jira-config.md > Static Field Values`) — if Brand and Domain are both null but Squad is populated, infer the domain from the squad name using the organizational structural reference (e.g., "CEC CLX" → "Career"). If inference is not confident, use the squad name as-is.
4. **All null** — omit domain label entirely for this signal

Record the derived domain label in the research artifact alongside the raw field values.

If all candidates are "Not relevant," report a confident negative with retrieval stats.

**Status signal weight** (for output ordering and reader interpretation):

| Status | Signal Weight | Interpretation |
| --- | --- | --- |
| Done | Strongest | Another team already built this — assess for leverage or duplication |
| 3 - GTM | Strong | Shipping imminently — high-confidence organizational investment |
| 2 - Experimentation | Medium-strong | Active development — team is committed |
| 1 - Opportunity Identification | Medium | Planned/explored — interest confirmed, investment not yet committed |
| Backlog | Weak | Queued but potentially stale — include for completeness, reader should discount |

Order output signals by status weight (strongest first).

### Phase 2.5: Rank and Curate for Output

Phase 2 may classify more signals as relevant than the reader needs. This phase selects the top signals for the Phase 3 output. The artifact (Phase 2.6) retains ALL classified signals for /jpd-push.

**Output cap:** Maximum 5 signals in Phase 3 output. If fewer than 5 classified as relevant, include all.

**Ranking dimensions** (apply these as reasoning lenses, not a scoring formula):

- **Actionability:** Would the reader need to coordinate with, align to, or build on this team's work? Direct overlap and convergence rank highest. Enablers rank higher when they represent a specific integration decision than when they're general infrastructure.
- **Status weight:** Done and GTM items are stronger signals (proven organizational investment). Opportunity Identification is interest, not commitment. Backlog is weakest.
- **Domain breadth:** Signals from different domains are more valuable together than multiple signals from one team's roadmap. Prefer breadth over depth.
- **Connection specificity:** A named integration point ("must accommodate multi-criteria scoring in grade passback") outranks a thematic similarity ("also works with assessments").

**Convergence curation:** Maximum 1 convergence group in the output. Select the group that spans the most domains and adds the strongest cross-cutting insight. The convergence synthesis line must state something the individual entries do not — a shared organizational need or strategic implication that emerges from the combination. If the synthesis would merely restate signal types and issue keys already visible in the entries, omit the convergence block.

**Exclusion reasoning:** For signals that classified as relevant but did not make the top 5, note them in the artifact under "Signals Reviewed and Excluded" with a brief rationale. This shows the skill's judgment and gives /jpd-push access to the full picture.

### Phase 2.6: Write Research Artifact

**Ad-hoc mode:** Skip this phase — no idea-scoped folder, no frontmatter to update. Jump directly to Phase 3 with signals presented in conversation only.

**Idea mode:**

Get today's date using `Bash(date:*)`: `date +%Y-%m-%d`

Create directory `Research/{idea-name}/` if it does not exist (use `Bash` to `mkdir -p`).

Write the full cross-domain results to `Research/{idea-name}/cross-domain-signals.md`. If a file already exists at that path from a prior run, write to `Research/{idea-name}/cross-domain-signals-{YYYY-MM-DD}.md` instead; if that also exists, append `-2`, `-3`, etc. Structure:

```markdown
---
type: incubator/research
agent: cross-domain
idea: {idea-name}
created: {YYYY-MM-DD}
---

# Cross-Domain Signals: {Idea Title}

**Analysis date:** {YYYY-MM-DD}

## Signals

{For each relevant signal:}
### [{issue-key}]({Atlassian base URL from jira-config.md}/browse/{issue-key}): {summary}
- **Brand:** {brand} | **Product Domain:** {product-domain} | **Squad:** {squad} | **Status:** {status} | **Quarter:** {quarter or "unset"}
- **Domain Label:** {derived domain label, or omit line if all source fields null}
- **Signal type:** {Direct overlap | Enabler/dependency | Convergence}
- **Connection:** {One sentence}

## Signals Reviewed and Excluded

{For each signal that classified as relevant but was cut in Phase 2.5:}
### [{issue-key}]({url}): {summary}
- **Excluded because:** {Brief rationale — why it didn't make the top 5}

{If no exclusions: omit this section.}

## Convergence Groups

{If any convergence groups detected:}
- **{Shared user need}:** [{issue-key}](link) ({Domain}), [{issue-key-2}](link) ({Domain})
  {One sentence synthesis}

{If no convergence groups: "None detected."}

## Retrieval Stats
Retrieved: {total} | After brand exclusion: {count} | Evaluated: {Phase 1.5 survivors} | Relevant: {N classified} | Output: {N in Phase 3}
```

Update the idea file frontmatter: append `Research/{idea-name}/cross-domain-signals.md` to the `research: []` array.

**Frontmatter update rules:**

- Read the current frontmatter to get the existing `research:` array
- Append the new path — including the dated suffix if this is an augment run
- Do NOT remove older dated-suffix entries from prior runs — augment artifacts coexist
- Do NOT change any other frontmatter fields (especially `stage:`)
- Use `Edit` to make the targeted frontmatter change

### Phase 3: Format Output

Phase 3 outputs only the signals selected in Phase 2.5 (maximum 5). This format is also used on the TL;DR card — the /develop orchestrator transfers it directly.

**When signals are found:**

```text
### Cross-Domain Signals
{N} ideas from other domains with possible functional overlap:
- [{issue-key}]({Atlassian base URL}/browse/{issue-key}) {summary} ({Domain Label}) — {Signal type}: {Connection sentence}
- [{issue-key}]({Atlassian base URL}/browse/{issue-key}) {summary} ({Domain Label}) — {Signal type}: {Connection sentence}

{If convergence group meets the quality bar — maximum 1:}
Convergence: {Group label} — [{issue-key}]({url}) ({Domain}), [{issue-key-2}]({url}) ({Domain}). {One sentence synthesis that adds insight the entries above do not state.}

Retrieved: {total} | After brand exclusion: {count} | Output: {N} | Artifact: {M classified}
```

Issue keys are linked using the Atlassian base URL from `jira-config.md`. Order signals by status weight (strongest first).

**When no signals are found:**

```text
### Cross-Domain Signals
No ideas from other domains with functional overlap found.

Retrieved: {total} | After brand exclusion: {count} | Evaluated: {Phase 1.5 survivors} | Relevant: 0
```

**When retrieval failed:**

```text
### Cross-Domain Signals
Could not check — {reason}.
This is NOT a confident negative. Cross-domain signals were not evaluated.
```

## Error Handling

| Scenario | Detection | Behavior | Output |
| --- | --- | --- | --- |
| MCP not authenticated (auth flow not yet attempted) | MCP tools unavailable on first query, no auth flow in progress | Surface auth URL, wait for user to complete OAuth, then retry the failed query once. Only stop if the retry also fails. | "Cross-domain discovery requires Atlassian MCP authentication. Open the auth URL, complete the flow, and the skill will retry automatically. If the retry fails, run `/mcp` to verify connection and re-invoke the skill." |
| MCP not authenticated (retry exhausted) | First query failed, auth flow completed by user, retry also failed | Stop | "Cross-domain discovery unavailable — Atlassian MCP authenticated but query still failed. Run `/mcp` to verify connection, then re-run." |
| MCP timeout | MCP call returns timeout error on any query | Stop. Do not retry. | "Could not check — Atlassian MCP timed out. Cross-domain signals were not evaluated. Restart Claude Code to refresh connection." |
| All partitions return 0 | All 5 status queries return empty | Warn — JPD should contain ideas | "Warning: JPD queries returned 0 results across all statuses. This is unexpected — verify MCP connection. Cross-domain signals could not be evaluated." |
| Some partitions fail | Some status queries succeed, others error | Continue with partial results | Note failed partitions in retrieval stats: "Note: {status} partition failed — {reason}." |
| Status partition truncated | A status query returns exactly 100 results | Continue, note informational | Note in retrieval stats: "{status} partition truncated at 100." |
| All results are own brand | Phase 1.5 Step A removes all candidates | Confident negative | Standard output with retrieval stats showing the drop |
| No results pass Phase 1.5 | Step B removes all remaining candidates | Confident negative | Standard output with retrieval stats |
| No results pass Phase 2 | All classified "Not relevant" | Confident negative | Standard output with retrieval stats |
| Phase 2 description fetch fails | Key-based query errors/times out | Degrade to summary-only | Add "(summary-only — description unavailable)" to affected signals |

**General principles:**

- Never silently swallow an error that changes confidence level
- Always distinguish "checked and clean" from "could not check"
- Partial results are better than no results — degrade gracefully
- MCP timeout is non-retryable within the same invocation

## Scope Boundaries

This skill does NOT:

- Change the idea's stage (enrichment only)
- Modify the idea file body (only appends to `research:` frontmatter array)
- Use internal strategy docs (that is Stream A's job)
- Use web search (that is Stream B's job)
- Assess impact dimensions (that is /develop's job)
- Recommend go/no-go decisions (that is a human decision)
- Retry failed MCP calls (connection state issue — non-retryable)

## Quality Standards

- **Precision over recall.** A false positive is worse than a missed connection.
- **Specific functional connections.** "Also uses AI" is not a connection. "Also building rubric evaluation for qualitative work" is.
- **Status-aware.** Done items signal existing capability to leverage. Backlog items signal interest, not commitment.
- **Honest confidence.** "Could not check" is never confused with "checked and found nothing."
- **Convergence is the highest-value signal.** Multiple teams solving the same problem independently means organizational energy is being spent — that is strategic intelligence.
- **Maximum 5 signals, maximum 1 convergence group.** The artifact keeps everything for /jpd-push. The output is curated for a product leader who scans and decides.
- **No general platform infrastructure.** Responsive design, accessibility compliance, and shipped foundational improvements that benefit many ideas are not signals. Only surface enablers with a specific integration point for THIS idea.
- **No same-team convergence.** Multiple items from one squad's roadmap are not convergence. Convergence requires different teams independently investing in the same need.

## Worked Example

The cache-route-optimization idea (`cache-route-optimization`) produced this output, using the fictional brand vocabulary from `org-taxonomy.sample.md` (Oakwood, Acorn, Burrow, Canopy). Study the reasoning, not just the format.

**6 candidates evaluated. 4 selected, 2 excluded.**

Selected:

- Multi-stop Route Builder Phase 2 (Oakwood, Done) — Enabler: adds intermediate-stop scheduling, directly enables the cache-checkpoint sequencing this idea requires. *Selected because: specific integration point, Done status (proven investment).*
- Enhanced Cache Tags Phase 3 (Acorn, Done) — Enabler: cache metadata schema improvements, foundational to any cache-route join logic. *Selected because: specifically load-bearing for a cache-routing idea — not general infrastructure.*
- Map Layer rotated terrain views (Oakwood, GTM) — Enabler: aligns territory views with seasonal foraging direction, exactly the orientation this idea's checkpoint scheduling depends on. *Selected because: specific to this idea's spatial layer, shipping imminently.*
- Burrow Inventory & Cache integration (Burrow, Opportunity Identification) — Convergence: Burrow building cross-cache inventory tracking — different angle on the same need for trustworthy cache state at routing time. *Selected because: different domain, same underlying need.*

Excluded:

- Enhanced Cache Tags pre-GA Tasks (Acorn, Done) — duplicative with Enhanced Cache Tags Phase 3, null description, low incremental value.
- Responsive Map UI (Oakwood, Done) — general UI infrastructure (responsive design, accessibility). Benefits every map feature, not specific to cache-route optimization.

Convergence group:
> Trustworthy cache state for downstream decisions — Multi-stop Route Builder Phase 2 (Oakwood), Enhanced Cache Tags Phase 3 (Acorn), Burrow Inventory & Cache (Burrow). Oakwood is investing in route infrastructure while Burrow is building cross-cache inventory — both need cache state to be trustworthy enough to drive downstream decisions, creating shared organizational interest that this idea can leverage.

*Why this convergence group works: the synthesis line states something the individual entries do not — "shared organizational interest" across domains. It answers "so what?" for the reader.*
