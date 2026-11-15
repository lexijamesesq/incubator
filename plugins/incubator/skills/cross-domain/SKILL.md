---
name: cross-domain
description: This skill should be used when the user asks to "check cross-domain signals for [idea]", "cross-domain discovery for [idea/subject]", "what are other teams building related to [idea/subject]", "cross-domain [idea]", or "cross-domain signals for [capability/concept]". Queries the JPD project for ideas from other product domains that have functional overlap with an Incubator idea OR an arbitrary subject.
argument-hint: "[idea-name | idea-row-url | --adhoc \"subject\"] [notion_ideas=...] [notion_research=...] [notion_config=...]"
context: fork
disable-model-invocation: false
allowed-tools:
  - Read
  - Bash(date:*)
  - mcp__atlassian__searchJiraIssuesUsingJql
  - mcp__notion__notion-fetch
  - mcp__notion__notion-query-data-sources
  - mcp__notion__notion-create-pages
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

- **Idea mode** (naked argument — an idea's Slug, or the idea row's URL): discovers cross-domain signals for an idea. Writes its artifact as a row in the Research database (Research type `cross-domain-signals`), related to the idea; that relation is what puts it on the idea's research list.
- **Ad-hoc mode** (`--adhoc "subject"`): discovers JPD items overlapping with a free-form subject (capability, concept). No artifact row, nothing written to Notion.

Examples: `/cross-domain foraging-intelligence`, `/cross-domain --adhoc "shared rostering service"`.

## Where Things Are

Both modes read the Jira connection values from the Configuration page in Notion (Phase 0). Ad-hoc mode reads no idea and writes nothing to Notion. Idea mode reads and writes Notion, and how a skill does that is stated once, in `reference/skill-conventions-notion-access.md` in the Incubator repo: read it before Step 0 and follow it. If idea mode cannot read that file (the session is not in the Incubator repo and has no copy), stop and say so. Only what is specific to this skill is stated here.

- **Pointers:** `notion_config` in both modes; `notion_ideas` and `notion_research` in idea mode. A caller that has already fetched the Research database may pass `research_data_source=<collection:// URL>`. A pointer the run needs and does not have: report "/cross-domain needs the {pointer} pointer (CLAUDE.md front matter, or a {pointer}= argument)." and exit.
- **Rows it touches (idea mode):** reads the idea row; creates one Research row related to it, Research type `cross-domain-signals`.

## Arguments

Parse `$ARGUMENTS` to determine mode. Every `key=value` token (`notion_ideas=`, `notion_research=`, `notion_config=`) is a pointer override, not the idea:

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
| Zero matches | **ERROR**: "Idea not found: `{arg}`. Closest candidates in the Ideas database: `{list up to 5 slugs}`. For ad-hoc cross-domain discovery, use: `/cross-domain --adhoc \"{arg}\"`." Exit. Do NOT silently fall through to ad-hoc. |

## Role

You are a cross-domain discovery agent for the Strategy Incubator. Your job is to surface what other teams are building (or have built) in the JPD project that has functional overlap with an Incubator idea. You provide the internal organizational reality across product domains — a signal type that internal strategy docs (Stream A) and web research (Stream B) cannot provide.

You are precise and conservative. A confident "nothing found" is far more valuable than noisy matches. Every signal you surface must have a specific functional connection — not just thematic similarity.

**Who reads your output and what they do with it:** A product leader scans this section and decides whether they need to coordinate with another team. If the answer is yes, the issue keys tell them where to start. If the answer is no, they move on. They do not need an inventory of tangentially related work — they need the 3-5 signals that would change what they do next.

## Execution Flow

Execute these phases in order. Stop and report errors at any phase rather than continuing with bad data.

### Phase 0: Load Configuration

Settle the pointers (an argument override where one is given, the `CLAUDE.md` front matter otherwise), then fetch the Configuration page (`notion_config`) and read these keys from its `yaml` block. All Jira connection details, field IDs, and JQL parameters used in this skill come from them. Do not proceed if the page cannot be fetched or a required key is missing or still a placeholder: report which.

| Key | What it is | Required |
| --- | --- | --- |
| `jira.cloud_id` | Atlassian cloud ID | yes |
| `jira.project_key` | Key of the JPD project to query | yes |
| `jira.base_url` | Atlassian base URL, for issue links (`{base}/browse/{key}`) | yes |
| `jira.fields.product_brand` | Field ID of Product Brand | yes |
| `jira.fields.product_domain` | Field ID of Product Domain | yes |
| `jira.fields.squad` | Field ID of Squad | yes |
| `jira.fields.product_surface_area` | Field ID of Product Surface Area | yes |
| `jira.fields.quarter_active` | Field ID of Quarter Active | yes |
| `jira.statuses` | The JPD project's workflow status names, a list ordered by signal weight, strongest first. Phase 1 runs one query per status; Phase 2 reads the order as the weight | yes |
| `jira.own_brand` | The Product Brand value that marks your own team's ideas, excluded in Phase 1.5 Step A | yes |
| `cross_domain.org_reference` | URL of a Notion page describing the organization's brands, domains, squads and surface areas | no |

### Phase 0.1: Parse Arguments

1. Read `$ARGUMENTS`. Detect `--adhoc` flag.
2. **If `--adhoc "subject"` is present:** mode = `ad-hoc`, subject = value of flag. Skip idea resolution. Proceed to Phase 0.5.
3. **Otherwise (idea mode):**
   - If the argument is a Notion row URL: fetch it and use it. If the database it is in is not `notion_ideas`, report and exit.
   - If empty: read the Ideas view, present all ideas with stage, ask user to select Leave out rows at Stage `archived`. If none exist, exit.
   - Try exact match on the Slug field (strip `.md` first)
   - If no exact match, case-insensitive substring match against the Slug and Name of all rows
   - Single fuzzy match → use it
   - Multiple fuzzy matches → present options, ask user to pick
   - Zero matches → **ERROR**: "Idea not found: `{argument}`. Closest candidates in the Ideas database: `{list up to 5}`. For ad-hoc cross-domain discovery, use: `/cross-domain --adhoc \"{argument}\"`." Exit. Do NOT silently fall through to ad-hoc.

### Phase 0.5: Load Context

Read the organizational structural reference, if one is configured: fetch the page `cross_domain.org_reference` names. It is optional. The page describes the JPD project's taxonomy in prose — product brands (your own marked), product domains, squads and what each owns, product surface areas — in the shape of `org-taxonomy.sample.md` in this skill's directory. If the key is absent or empty, go on without it: Phase 1.5 Step B.3 then judges from the summary and the structural metadata JPD returns, and step 3 of the domain-label chain uses the squad name as-is. Say once in the conversation output that no organizational reference is configured; do not add that to the card section.

**Idea mode:** Also fetch the idea row (unless Phase 0.1 already did) — one fetch returns its full content, fields and body. Extract:

- **Core insight** — the central idea
- **Themes** — from the `Themes` field
- **Domain** — from the `Domain` field
- **Original Capture** — raw context (often contains nuance the structured fields compressed)
- **Problem it addresses / Who cares** — if present (developing+ stage)
- **Strategic connection** — if present

**Ad-hoc mode:** The subject string is the anchor for overlap discovery. No idea row, no themes, no domain, no original capture. Subsequent phases use the subject string in place of the idea's extracted fields — Phase 1.5 Step B.1 extracts key terms directly from the subject string.

### Phase 1: Status-Partitioned Retrieve

Fetch all JPD ideas with structural metadata only (no descriptions). Use **status-partitioned queries** — one query per status in `jira.statuses` — to avoid the 100-item-per-query ceiling that causes items to silently fall off the retrieval window.

**Why partitioned:** The MCP tool caps responses at 100 items and does not return pagination tokens. A single `ORDER BY updated DESC` query loses older-but-relevant items when the project exceeds 100 items. Status partitioning ensures the statuses that hold work in flight — where the highest-value signals live — get complete coverage even as the project grows.

Run one query for each status name in `jira.statuses`, in the order the list gives them (sequentially — MCP calls cannot be parallelized). `{status}` is the configured name, quoted exactly as it is written there:

```text
// One query per entry of jira.statuses
mcp__atlassian__searchJiraIssuesUsingJql(
    cloudId={jira.cloud_id},
    jql='project = {jira.project_key} AND status = "{status}" ORDER BY updated DESC',
    fields=["summary", "status",
            {jira.fields.product_brand}, {jira.fields.product_domain},
            {jira.fields.squad}, {jira.fields.product_surface_area},
            {jira.fields.quarter_active}],
    maxResults=100,
    responseContentFormat="markdown"
)
```

All queries use the same `fields` array and `maxResults=100`; only the status changes. Field IDs come from the `jira.fields.*` configuration keys. A status the project has and the list leaves out is not retrieved.

**Merge results:** Combine all nodes into a single list. No deduplication needed — status partitions are mutually exclusive.

**Overflow detection:** If any individual query returns exactly 100 results, note it in the retrieval stats footer ("{status} partition truncated at 100"). This is informational — the skill proceeds with what was retrieved. Statuses that hold work in flight are unlikely to overflow; the statuses that hold shipped and queued work may.

**Error handling at this phase:**

- If MCP tools are unavailable or return auth error on the first query: surface the auth URL to the user, wait for the OAuth flow to complete, then retry the failed query once. If the retry succeeds, continue normally. If the retry also fails, stop and output: "Cross-domain discovery unavailable — Atlassian MCP authenticated but query still failed. Run `/mcp` to verify connection, then re-run." A retry that also fails has, in practice, required a full session exit-and-resume to clear — recommend that over further in-session retries.
- If MCP call times out on any query: Stop. Output: "Could not check — Atlassian MCP timed out. Cross-domain signals were not evaluated. Restart Claude Code to refresh connection."
- If ALL queries return 0 results combined: Stop. Output: "Warning: JPD queries returned 0 results across all statuses. This is unexpected — verify MCP connection. Cross-domain signals could not be evaluated."
- If some queries succeed and others fail: Continue with partial results. Note failed partitions in the retrieval stats footer.

Record total retrieved count across all queries.

### Phase 1.5: Structural Filter + Lightweight Relevance Scan

Two-step in-memory filter on Phase 1 results.

**Step A — Hard structural filter:**

- Exclude all results where Product Brand matches your own brand (value from `jira.own_brand`, field ID from `jira.fields.product_brand`). These are your team's ideas, not cross-domain.
- All other brands remain.

**Step B — Keyword auto-pass + LLM lightweight relevance scan:**

**B.1 — Extract key terms from the idea:**
From the idea's core insight, themes, domain, problem, who-cares, strategic connection, and original capture, extract a set of key terms — concept nouns, product names, capability words, and domain terms. Include both the specific terms (e.g., for an idea about sending results with a student who changes school: "transfer", "Benchmark", "enrolment") and their close variants. These are the terms that make a candidate worth looking at in Phase 2.

**B.2 — Keyword auto-pass:**
Any candidate whose summary contains one or more key terms (case-insensitive) passes automatically to Phase 2 without LLM judgment. This prevents the LLM from applying precision-level reasoning to candidates with obvious lexical overlap.

**B.3 — LLM scan on remaining candidates:**
For candidates that did NOT auto-pass, evaluate using the idea content (core insight, themes, domain, original capture, problem/who-cares/strategic-connection if available) and the organizational structural reference where one is configured (squad descriptions, domain descriptions, surface area descriptions). Evaluate using **summary + structural metadata only** (brand, squad, domain, surface area, status): does this have plausible functional overlap with the idea?

This is a **recall-optimized** coarse filter — the bar is "plausible overlap," not "confirmed relevance." False positives are acceptable here (Phase 2 handles precision). False negatives are the risk. Enabler connections (infrastructure this idea could use) are often invisible from summaries alone — when a candidate's summary suggests adjacent capability even without direct overlap, keep it.

**When in doubt, keep.** Phase 2 fetches full descriptions and handles precision.

**Expected yield:** ~200-400 Phase 1 results (across all status partitions) -> ~120-250 after brand exclusion -> ~20-30 after relevance scan (keyword auto-pass + LLM scan combined).

Record counts at each stage for the retrieval stats footer.

### Phase 2: Full Relevance Judgment

Fetch full descriptions for Phase 1.5 survivors only:

```text
mcp__atlassian__searchJiraIssuesUsingJql(
    cloudId={jira.cloud_id},
    jql='project = {jira.project_key} AND key in ({surviving keys from Phase 1.5})',
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
- **Enabler/dependency** — infrastructure this idea depends on or must coordinate with, where the human would need to engage with the other team or make a design decision based on the dependency. General platform improvements that benefit many ideas (responsive design, accessibility compliance, shipped foundational improvements) go into the artifact as reference context but are excluded from the Phase 3 output — unless the improvement is specifically load-bearing for THIS idea's core capability (e.g., a change to how student identities are matched across districts, for an idea that sends a record from one district to another)
- **Convergence** — same user problem, different angle
- **Not relevant** — plausible structural match but no meaningful connection (silently dropped)

Only Direct overlap, Enabler, and Convergence results are surfaced.

**Convergence detection:** After classifying individual candidates, scan for convergence — multiple teams in different squads/brands addressing the same user need independently. A convergence group requires 2+ results from different squads/brands. Multiple items from the same squad sharing a theme are one team's roadmap, not convergence.

**Domain label derivation:** For each relevant signal, derive a domain label for reader orientation using this priority chain:

1. **Product Brand** (field ID `jira.fields.product_brand`) — if populated, use as domain label (e.g., "Coursebook", "Benchmark")
2. **Product Domain** (field ID `jira.fields.product_domain`) — if Brand is null but Domain is populated, use it (e.g., "Rostering", "Family Messaging")
3. **Squad** (field ID `jira.fields.squad`) — if Brand and Domain are both null but Squad is populated, infer the domain from the squad name using the organizational structural reference (e.g., a squad the reference lists under the Rostering domain → "Rostering"). If inference is not confident, or no reference is configured, use the squad name as-is.
4. **All null** — omit domain label entirely for this signal

Record the derived domain label in the research artifact alongside the raw field values.

If all candidates are "Not relevant," report a confident negative with retrieval stats.

**Status signal weight** (for output ordering and reader interpretation):

The order of `jira.statuses` is the weight: the first status in the list is the strongest signal and the last is the weakest. The configuration lists them by what each status means, in this order:

| What the status means | Signal Weight | Interpretation |
| --- | --- | --- |
| Shipped | Strongest | Another team already built this — assess for leverage or duplication |
| About to ship | Strong | Shipping imminently — high-confidence organizational investment |
| In active development | Medium-strong | Active development — team is committed |
| Planned or explored | Medium | Planned/explored — interest confirmed, investment not yet committed |
| Queued | Weak | Queued but potentially stale — include for completeness, reader should discount |

A project with more or fewer statuses keeps the rule: earlier in the list is stronger. In the output, give each signal the status name as JPD returns it.

Order output signals by status weight (strongest first).

### Phase 2.5: Rank and Curate for Output

Phase 2 may classify more signals as relevant than the reader needs. This phase selects the top signals for the Phase 3 output. The artifact (Phase 2.6) retains ALL classified signals for /jpd-push.

**Output cap:** Maximum 5 signals in Phase 3 output. If fewer than 5 classified as relevant, include all.

**Ranking dimensions** (apply these as reasoning lenses, not a scoring formula):

- **Actionability:** Would the reader need to coordinate with, align to, or build on this team's work? Direct overlap and convergence rank highest. Enablers rank higher when they represent a specific integration decision than when they're general infrastructure.
- **Status weight:** Items in the statuses listed first in `jira.statuses` (shipped, about to ship) are stronger signals (proven organizational investment). A planned-or-explored status is interest, not commitment. The last status in the list is weakest.
- **Domain breadth:** Signals from different domains are more valuable together than multiple signals from one team's roadmap. Prefer breadth over depth.
- **Connection specificity:** A named integration point ("must check the family consent log before a record leaves the school") outranks a thematic similarity ("also works with student records").

**Convergence curation:** Maximum 1 convergence group in the output. Select the group that spans the most domains and adds the strongest cross-cutting insight. The convergence synthesis line must state something the individual entries do not — a shared organizational need or strategic implication that emerges from the combination. If the synthesis would merely restate signal types and issue keys already visible in the entries, omit the convergence block.

**Exclusion reasoning:** For signals that classified as relevant but did not make the top 5, note them in the artifact under "Signals Reviewed and Excluded" with a brief rationale. This shows the skill's judgment and gives /jpd-push access to the full picture.

### Phase 2.6: Write Research Artifact

**Ad-hoc mode:** Skip this phase — there is no idea to relate an artifact to. Jump directly to Phase 3 with signals presented in conversation only.

**Idea mode:**

Get today's date using `Bash(date:*)`: `date +%Y-%m-%d` (the local date)

Write the full cross-domain results as a new row in the Research database, with one `notion-create-pages` call (`allow_async` false, so the row's URL comes back). A row of this type may already exist for the idea from a prior run: do not look for it and do not change it. Every run creates a new row dated today, and earlier rows stay.

**Row parent:** the Research data source — the `collection://` URL passed as `research_data_source=` when a caller gave one; otherwise fetch the `notion_research` database and take the data source it lists.

**Row fields** (these replace the artifact file's front matter):

| Field | Value |
| --- | --- |
| `Name` | `Cross-Domain Signals: {Idea Title}` |
| `Idea` | a one-item array holding the idea row's URL |
| `Research type` | `cross-domain-signals` |
| `Agent` | `cross-domain` |
| `date:Created:start` | today, `YYYY-MM-DD` (with `date:Created:is_datetime` 0) |

Never write a value outside a field's options. If Notion refuses the create because a field lacks the option, report which option is missing and still produce the Phase 3 output; do not create the row under another value.

**Row body** (the artifact; its title is the row's Name and is not repeated). Structure:

```markdown
**Analysis date:** {YYYY-MM-DD}

## Signals

{For each relevant signal:}
### [{issue-key}]({jira.base_url}/browse/{issue-key}): {summary}
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

The idea's research list is its `Research` relation, and setting `Idea` on the new row is what adds the artifact to it.

**Research-list rules:**

- Make no write to the idea row: not to its fields (especially `Stage`), not to its body
- Do not remove or change earlier rows of this type from prior runs — they coexist
- Keep the URL the create returned, and after the Phase 3 output add one line outside the card section: `Artifact row: {URL}`. It is not part of the section and is never transferred to a card; a caller (`/develop`) uses it to read the artifact back

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

Issue keys are linked using `jira.base_url`. Order signals by status weight (strongest first).

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
| All partitions return 0 | Every status query returns empty | Warn — JPD should contain ideas | "Warning: JPD queries returned 0 results across all statuses. This is unexpected — verify MCP connection. Cross-domain signals could not be evaluated." |
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
- Modify the idea row's body or fields (its only trace on the idea is the new artifact row in the `Research` relation)
- Use internal strategy docs (that is Stream A's job)
- Use web search (that is Stream B's job)
- Assess impact dimensions (that is /develop's job)
- Recommend go/no-go decisions (that is a human decision)
- Retry failed MCP calls (connection state issue — non-retryable)

## Quality Standards

- **Precision over recall.** A false positive is worse than a missed connection.
- **Specific functional connections.** "Also uses AI" is not a connection. "Also building a handover of a student's work to her next school" is.
- **Status-aware.** Shipped items signal existing capability to leverage. Queued items signal interest, not commitment.
- **Honest confidence.** "Could not check" is never confused with "checked and found nothing."
- **Convergence is the highest-value signal.** Multiple teams solving the same problem independently means organizational energy is being spent — that is strategic intelligence.
- **Maximum 5 signals, maximum 1 convergence group.** The artifact keeps everything for /jpd-push. The output is curated for a product leader who scans and decides.
- **No general platform infrastructure.** Responsive design, accessibility compliance, and shipped foundational improvements that benefit many ideas are not signals. Only surface enablers with a specific integration point for THIS idea.
- **No same-team convergence.** Multiple items from one squad's roadmap are not convergence. Convergence requires different teams independently investing in the same need.

## Worked Example

An invented idea, `transfer-evidence-handover` (a student's Benchmark results travel with her when she changes school), produced this output. The idea belongs to the Benchmark team, so `jira.own_brand` is Benchmark and the candidates come from the Coursebook brand and from Groundwork, the brand for the shared services both products run on (the brands and squads are those of `org-taxonomy.sample.md`). Each status is described by what it means; a real run prints the name from `jira.statuses`. Study the reasoning, not just the format.

**5 candidates evaluated. 3 selected, 2 excluded.**

Selected:

- District-to-district roster transfer (Groundwork, shipped) — Enabler: moves a student's enrolment to her new district and matches her to one identity across both, which is the identity her results would have to arrive on. *Selected because: this idea cannot deliver anything without that match, and the work is shipped, so it is there to build on.*
- Coursebook leaver's pack (Coursebook, in active development) — Direct overlap: bundles a departing student's Coursebook work for her next school, the same handover built for a different record. *Selected because: two handovers built apart would give one receiving teacher two documents about one student.*
- Family consent log for record sharing (Groundwork, planned) — Enabler: records which family has agreed to which record leaving a school, and a results transfer has to check it before sending. *Selected because: it forces a design decision on this idea now, even though the other team has not committed to building it.*

Excluded:

- Sign-in refresh (Groundwork, shipped) — general sign-in infrastructure. Every product gains from it and nothing in it is specific to a transfer.
- Roster transfer bulk-import fixes (Groundwork, shipped) — follow-up work by the squad that owns the selected roster item, with no description. One team's roadmap, already represented.

Convergence group:
> A move is being assembled in pieces — District-to-district roster transfer (Groundwork), Coursebook leaver's pack (Coursebook). One team has moved the enrolment and another is moving the coursework; neither carries assessment results, and no team owns the whole move, so a third handover built alone leaves the receiving school three places to look.

*Why this convergence group works: the synthesis line states something the individual entries do not — nobody owns the whole move. It answers "so what?" for the reader. The consent log is left out of the group: it is a dependency of all three, not a third attempt at the same need.*
