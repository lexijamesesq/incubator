---
name: jpd-push
description: This skill should be used when the user asks to "push [idea] to JPD", "push [idea name]", "jpd push [idea]", or "push [idea] to JPD". Pushes a developed idea to JPD for stakeholder visibility. One-directional push with human review gate.
argument-hint: [idea-name]
context: conversation
disable-model-invocation: false
allowed-tools:
  - Read
  - Edit
  - Write
  - Glob
  - Grep
  - Bash(date:*)
  - mcp__atlassian__createJiraIssue
  - mcp__atlassian__editJiraIssue
  - mcp__atlassian__transitionJiraIssue
  - mcp__obsidian__read_note
  - mcp__obsidian__read_multiple_notes
  - mcp__obsidian__update_frontmatter
  - mcp__obsidian__get_frontmatter
  - mcp__obsidian__patch_note
  - mcp__claude_ai_Google_Drive__create_file
  - mcp__claude_ai_Google_Drive__search_files
  - mcp__claude_ai_Google_Drive__get_file_metadata
---

# /jpd-push — Push Idea to JPD

Pushes a developed idea to JPD for stakeholder visibility. One-directional — no automated sync-back. Supports first push (create) and re-push (update).

## Invocation

```text
/jpd-push [idea-name]
```

- Required argument: the name of a developing-or-later idea file in `Ideas/`
- If no argument provided: list eligible ideas and ask user to pick
- Examples: `/jpd-push foraging-intelligence`, `/jpd-push cache-optimization`

## Arguments

Parse `$ARGUMENTS` to resolve the target idea file and any flags.

**Argument structure:** `[idea-name] [flags]` — idea-name is the positional argument; flags are space-separated and follow.

**Recognized flags:** None currently.

Unknown flags should be reported as an error and exit before resolution proceeds — e.g., `Unknown flag: '--foo'. No flags recognized.` This prevents typos from silently no-op'ing.

**Sidecar correction:** When sidecar content needs fixing (corrected DB label, regenerated artifact, typo), do NOT use a versioned-folder regeneration pattern. The sidecar is a folder, not a single Doc — the folder URL is canonical and doesn't need to change for content fixes. Use the in-place correction sub-flow under Step 5 instead. Conversational invocation is fine; no flag is required.

**Idea-name resolution rules** (applied after flag parsing, against the positional argument):

| Input | Behavior |
| ------- | ---------- |
| Empty | List all developing-or-later ideas in Ideas/, ask user to select |
| `idea-name` | Resolve to `Ideas/{idea-name}.md` |
| `idea-name.md` | Strip `.md`, resolve as above |

**Fuzzy matching:** If exact match fails, list all `.md` files in Ideas/ and find filenames containing the argument as a substring (case-insensitive). If exactly one match, use it. If multiple matches, present options. If zero matches, report and exit.

## Reference Material

`incubator-reference.md` is a thin section index. Load only the `reference/` section files this skill needs:

- `reference/jpd-integration.md` — JPD template alignment, push criteria, sync-tracking fields, sync-back policy
- `reference/frontmatter-schema.md` — `jira-key` / `jira-pushed-at` / `jira-sidecar-url` fields, `themes` as labels

## Execution Flow

### Step 0: Load Configuration

Read `jira-config.md` from the Incubator project root (`Projects/Incubator/jira-config.md`) via `mcp__obsidian__read_note`. All Jira connection details, field IDs, and option IDs used in this skill come from that file. Do not proceed if the file cannot be read.

Also read `Projects/Incubator/CLAUDE.md` Configuration > External References block to resolve `incubator.jpd_sidecars_folder_id` (used in Step 3c), `incubator.research_db_label` (used in Step 3c sidecar substitution), and the strategy doc `path` → `external_url` mappings (used in Step 3 link translation).

### Step 1: Load and Validate

Read the idea file via `mcp__obsidian__read_note` (vault `.md` files are blocked from generic Read by the vault redirect hook — Obsidian MCP is the canonical reader for vault content). Verify all push prerequisites:

**Required for push:**

- `stage` is `developing`, `drafting`, `refining`, or `complete`
- All five impact dimensions are non-null (`customer-sentiment`, `user-experience`, `revenue-potential`, `industry-disruption`, `strategic-alignment`)
- Body contains populated sections: Core insight, Problem it addresses, Who cares, Strategic connection, Opportunity Assessment table, Research Summary

**If any prerequisite fails:** Report exactly what's missing and exit. Do not proceed with incomplete ideas.

### Step 2: Detect Push Type

Check the idea's frontmatter for `jira-key`:

- **`jira-key` is null or absent:** This is a **first push** — will create a new issue.
- **`jira-key` has a value (e.g., {issue-key}):** This is a **re-push** — will update the existing issue.

Report which type this is before proceeding.

### Step 3: Prepare Payload

Extract and transform the idea content into JPD fields:

**Summary:** The idea title from the H2 heading (e.g., `## Cohort and Peer Intelligence` becomes `Cohort and Peer Intelligence`).

**Description:** Restructure the TL;DR body into JPD-compatible headings. Content is transferred verbatim — no generative rewriting. Only the heading structure changes. Exclude `### Original Capture` (internal provenance only). If a Cross-Domain Signals section will be included (see Step 3a), strip any cross-domain bullets from the Research Summary to avoid redundancy — the dedicated section is the single place for that data in JPD.

Map the TL;DR sections into this structure:

```markdown
## What
{Core insight text — verbatim, strip bold label prefix}
{Problem it addresses text — verbatim, strip bold label prefix}

## Who
{Who cares text — verbatim, strip bold label prefix}

## Why
{Strategic connection text — verbatim, strip bold label prefix}

## Opportunity Assessment
{Table — verbatim from card}

## Research Summary
{Findings — verbatim from card}

[Full development research](<<SIDECAR_URL>>)

The `<<SIDECAR_URL>>` token is a literal placeholder. On first push, Step 3c stages content with this placeholder in the description; Step 5a creates the JPD issue with the placeholder still in place; Step 5b creates the sidecar Google Doc; Step 5c calls editJiraIssue to replace `<<SIDECAR_URL>>` with the real `viewUrl`. On re-push, the description is built with `jira-sidecar-url` from frontmatter substituted directly (no placeholder, no extra edit).

## Cross-Domain Signals
{Mirror the card's `### Cross-Domain Signals` section verbatim — see Step 3a. Omit if absent on card.}

## Thought Outline
{Content — verbatim from card}

## Disruptive Reframing
{Disruptive divergent angle — see Step 3b. Omit if no divergent-angles artifact exists.}

## Buildable Surface
{Include ONLY if Buildable Surface section exists on the card. Transfer verbatim. Omit section entirely if not present on card.}

## Open Questions
{Content — verbatim from card}
```

"Strip bold label prefix" means: `**Core insight:** Assessment platforms treat...` becomes `Assessment platforms treat...` — remove the `**Label:**` prefix since the heading now provides the context.

**Link translation:** Idea cards may use internal file paths for strategy doc references. Before building the description, replace these with external URLs so links resolve in Jira. The link translation table is configured in CLAUDE.md under Configuration > External References — each external reference entry includes both a local path and an external URL. Match on the local path substring within markdown links and replace with the corresponding external URL, preserving the link text.

Apply to the entire description body.

### Step 3a: Cross-Domain Signals section (mirror card or self-heal from artifact)

The default path is card-canonical: if the card body has a `### Cross-Domain Signals` section, transfer it verbatim into the JPD body as `## Cross-Domain Signals` (heading level adjusted from h3 to h2; content preserved exactly). The card carries the curated 5 signals + 1 convergence group selected by the cross-domain skill's Phase 2.5 ranking — JPD shows the same curated set. The full classified set (including any signals excluded from card output, plus retrieval stats) lives in the Research Sidecar (Step 3c) for stakeholders who want depth.

**Self-heal fallback** — if the card has NO `### Cross-Domain Signals` section but `Research/{idea-name}/cross-domain-signals.md` exists, derive the section from the artifact and patch it onto the card BEFORE building the JPD payload. This handles cards developed before /cross-domain became a standard /develop step (architecture migration).

Self-heal procedure:

1. Read the artifact via `mcp__obsidian__read_note`. Extract signals from the `## Signals` section only (NOT from `## Signals Reviewed and Excluded`). Extract convergence groups from `## Convergence Groups`.

2. Apply the curation cap: 5 signals maximum, 1 convergence group maximum.
   - **If the artifact has ≤5 signals under `## Signals`:** use all of them.
   - **If the artifact has >5 signals under `## Signals`:** rank candidate signals using the 4-criterion heuristic defined in `claude/skills/cross-domain/SKILL.md` Phase 2.5 (the canonical source) — read that section and apply it to select the top 5.
   - **Convergence:** if the artifact has multiple convergence groups, pick the one that spans the most domains and whose anchor signals remain in the kept-5.

3. Format the curated set into a `### Cross-Domain Signals` section using the canonical card template:

   ```text
   ### Cross-Domain Signals
   {N} ideas from other domains with possible functional overlap:
   - [{issue-key}]({Atlassian base URL from jira-config.md}/browse/{issue-key}) {Issue Title} ({Domain Label}) — {Signal type}: {Connection text — verbatim from artifact's **Connection:** field}
   - ...

   Convergence: {theme} — [{issue-key}](URL) ({Domain Label}), [{issue-key}](URL) ({Domain Label}). {Convergence narrative — verbatim from artifact}.
   ```

   For each signal, derive the parenthetical Domain Label using the same priority chain /cross-domain uses: Brand → Product Domain → Squad → omit. If the artifact's `**Domain Label:**` line is populated, use that value directly.

4. Patch the new section into the card body BETWEEN `### Research Summary` (and its content) and `### Thought Outline` using `mcp__obsidian__patch_note`. Replace the boundary string `\n\n### Thought Outline\n` with `\n\n{new section}\n\n### Thought Outline\n`. Before patching, read the card and locate the actual anchor text; if the exact string with expected whitespace isn't found, try single-newline variants. If still ambiguous or not found, halt and report rather than guessing.

5. Re-read the card to confirm the section is present and correctly positioned. If verification fails, halt and report — do not proceed to JPD push with an unconfirmed card edit.

6. Continue with JPD payload construction — Step 3a's main path now picks up the section that was just inserted.

**If neither card section nor artifact exists:** omit the JPD Cross-Domain Signals section entirely. This is the only case where the section is silently dropped.

**Self-heal scope:** This fallback only inserts a missing section. It does NOT re-curate cards that already have a section but with stale content (e.g., >5 signals, malformed entries). For those cases, the card edit is a manual operation outside this skill.

#### Step 3b: Disruptive Reframing section (mirror card or self-heal from artifact)

The default path is card-canonical: if the card body has a `### Disruptive Reframing` section, transfer it verbatim into the JPD body as `## Disruptive Reframing` (heading level adjusted h3→h2; content preserved exactly), then append the `[Full development research](<<SIDECAR_URL>>)` link trailer below the distillation. The card carries the 2-3 sentence distillation produced by /develop Step 5d — JPD shows the same content. The link trailer is a JPD-only addition; the card version does not include it.

**Self-heal fallback** — if the card has NO `### Disruptive Reframing` section but `Research/{idea-name}/divergent-angles.md` exists, derive the section from the artifact and patch it onto the card BEFORE building the JPD payload. This handles cards developed before /develop Step 5d became standard (architecture migration).

Self-heal procedure:

1. Read the artifact via `mcp__obsidian__read_note`. Locate "## The Disruptive One" — the divergent-thinking skill identifies one of its 3–5 angles as the disruptive frame; that's the one to inline.

2. Distill the **2–3 sentence insight** from that angle's "The connection" and "What it opens up" content. Stay close to the artifact's language; do not generatively rewrite.

3. Format the distillation into a `### Disruptive Reframing` section using the canonical card template:

   ```text
   ### Disruptive Reframing
   **{Disruptive Angle Title}** — {2-3 sentence insight summarizing the connection and what it opens up}
   ```

   No link trailer in the card section — that's a JPD-only addition.

4. Patch the new section into the card body BETWEEN `### Thought Outline` (and its content) and the next `###` heading (which will be `### Buildable Surface` if it exists, otherwise `### Open Questions`) using `mcp__obsidian__patch_note`. Anchor on the next `###` heading after Thought Outline and insert the new section before it. Before patching, read the card and locate the actual anchor text; if the exact string with expected whitespace isn't found, try single-newline variants. If still ambiguous or not found, halt and report rather than guessing.

5. Re-read the card to confirm the section is present and correctly positioned. If verification fails, halt and report — do not proceed to JPD push with an unconfirmed card edit.

6. Continue with JPD payload construction — Step 3b's main path now picks up the section that was just inserted, and appends the `[Full development research](<<SIDECAR_URL>>)` link trailer for JPD.

**If neither card section nor artifact exists:** omit the JPD Disruptive Reframing section entirely.

**Self-heal scope:** This fallback only inserts a missing section. It does NOT re-curate cards that already have a section but with stale content. For those cases, the card edit is a manual operation outside this skill.

Avoid the word "leveraged" as a section heading — it's on the persona's kill list and conveys nothing concrete; "Disruptive Reframing" names what the section actually is.

##### Step 3c: Stage Research Sidecar content (first push only)

If this is a first push (no `jira-key` in frontmatter), stage the four sidecar `.md` files in memory here. Folder + file creation happens in Steps 5b/5c — after the JPD issue is created and `jira-key` is known — so each file's frontmatter can carry a working back-link to the JPD issue. The Drive MCP doesn't expose a content-edit tool, so each create_file call must be made with the JPD reference already substituted in.

The sidecar architecture is **one folder per pushed idea, four `.md` files per folder** — one per research stream. The folder name is `{jira-key} - {Idea Title}` (with `/` characters in the title replaced with `-`; other Unicode preserved). The Research Summary link in the JPD body points to the folder URL.

1. Read the four primary research artifacts in parallel via `mcp__obsidian__read_multiple_notes`:
   - `Research/{idea-name}/edtech-market-analysis.md`
   - `Research/{idea-name}/tam-estimate.md`
   - `Research/{idea-name}/educator-evaluation.md`
   - `Research/{idea-name}/divergent-angles.md`

2. Skip any artifact that doesn't exist (the corresponding /develop agent must have failed). Note any skipped artifacts in the review gate output for transparency.

3. For each artifact, strip the existing YAML frontmatter and prepend a sidecar-specific frontmatter block. The frontmatter uses literal placeholders for both the JPD reference (`<<JIRA_KEY>>`, `<<JIRA_URL>>` — substituted in Step 5c) and the research database label (`<<RESEARCH_DB_REF>>` — substituted at staging time using `incubator.research_db_label` from CLAUDE.md). The body keeps the artifact's existing H1 and content untouched.

When staging, replace `<<RESEARCH_DB_REF>>` in each row's `sources` block with the value of `incubator.research_db_label` from CLAUDE.md (Configuration > External References). This abstraction keeps the public skill file free of installation-specific database identifiers while letting the generated sidecar content carry the concrete reference stakeholders need. If the config key is missing, omit the entire research-database source line for that file (the `/edtech-sme`, `/tam-estimate`, or `/educator-sme` line stays — only drop the database row).

**Per-stream sidecar template:**

```markdown
---
type: incubator/research-sidecar
idea: {idea-name}
jira-key: <<JIRA_KEY>>
jira-url: <<JIRA_URL>>
stream: {stream-slug}
sources:
{sources-block — see mapping below}
generated: {YYYY-MM-DD via Bash(date:*)}
---

{full body of the artifact, frontmatter stripped, H1 onward preserved}
```

**Per-stream slug + sources mapping:**

| File name | stream slug | sources |
| --- | --- | --- |
| `EdTech Market Analysis.md` | `edtech-market-analysis` | `- /edtech-sme agentic researcher (web research + competitor evaluation)`<br>`- <<RESEARCH_DB_REF>> — competitive landscape findings` |
| `TAM Estimate.md` | `tam-estimate` | `- /tam-estimate agentic researcher (top-down + bottom-up market sizing)`<br>`- <<RESEARCH_DB_REF>> — market-sizing findings` |
| `Educator Evaluation.md` | `educator-evaluation` | `- /educator-sme agentic researcher (classroom-reality evaluation)`<br>`- <<RESEARCH_DB_REF>> — customer-evidence findings` |
| `Divergent Angles.md` | `divergent-angles` | `- /divergent-thinking agentic researcher (cross-domain pattern matching)` |

The Divergent Angles file has only one source — `/divergent-thinking` does not write findings to Snowflake by design (creative reframing is excluded from the research database).

The Research Summary link line in the JPD body description (built in Step 3) uses the literal placeholder `<<SIDECAR_URL>>` that's substituted in Step 5d after the folder is created and its URL is known.

**Re-push behavior:** On re-push (`jira-key` already present), do NOT regenerate the sidecar by default. Read `jira-sidecar-url` from the idea file frontmatter and reuse it directly in the JPD body description's "Full development research:" link line — no Drive call needed.

If the frontmatter `jira-sidecar-url` is missing on a re-push (i.e., the idea was first pushed before the sidecar feature existed, or the field was removed), fall back to one of: (a) treat the re-push as a sidecar-bootstrap and run Step 3c to generate a v1 sidecar now, then store the URL in frontmatter, or (b) prompt the user at the review gate to confirm bootstrap. Default to (a) when the four research artifacts exist; prompt only when one or more are missing.

For sidecar content correction (corrected DB label, regenerated artifact, typo): see "Re-push with sidecar correction (in-place)" under Step 5. The folder URL stays the same; only the affected files are recreated after the human deletes them in the Drive UI. No JPD edit, no frontmatter update.

**Executive Summary:** The Core insight sentence, plain text only (strip bold markers). Max 255 characters — if the core insight exceeds this, condense to fit without losing the key claim. Show the condensed version in the review gate.

**AI Feature:** If `themes` array contains any value starting with `ai-`, set to `1` (numeric). Otherwise omit.

**Domain Objective:** Select the single best-fit objective based on the idea's content and impact dimensions. Objective labels and their option IDs are in `jira-config.md > Domain Objective Mapping`.

Format as: `[{"id": "{option_id}"}]`

Use the impact dimensions as signals to select the best-fit objective from the mapping table. When ambiguous, pick the strongest signal and note the reasoning.

**Labels:** The `themes` array values from frontmatter, as-is.

**Static fields:** Apply all static field values from `jira-config.md > Static Field Values`. That table defines the field ID, option ID, and format for each static field (Product Brand, Product Domain, Squad, Product Surface Area, 2026 Roadmap Priority, Quarter Active).

### Step 4: Human Review Gate

Present the complete proposed payload to the human:

```text
**Push preview: {idea-name}**
Type: {First push | Re-push to {jira-key}}

**Summary:** {title}

**Executive Summary:** {core insight}

**Domain Objective:** {objective label} — {one-line rationale}

**AI Feature:** {Yes | No}

**Labels:** {comma-separated themes}

**Static fields:** {list each static field from jira-config.md with its configured value}

**Description body:**
{the extracted description, shown in full}

---
Confirm to push, or provide overrides (e.g., "change Surface Area to X", "change Roadmap Priority to Y").

**Placeholders in description preview:** On first push, the preview shows `<<SIDECAR_URL>>` in two places — the Research Summary trailer and the Disruptive Reframing trailer (both render as `[Full development research](<<SIDECAR_URL>>)`). Both placeholders are replaced with the real Drive folder URL in Step 5d after the sidecar folder is created — the JPD issue will land with working links, not literal tokens. The same applies to `<<JIRA_KEY>>` and `<<JIRA_URL>>` in the staged sidecar file frontmatter (substituted in Step 5c once `jira-key` is known). Mention this in the review output so the user isn't surprised.
```

**Wait for human confirmation.** Do not push without explicit approval.

**Overrides:** If the human provides overrides for Surface Area, Roadmap Priority, or Domain Objective, apply them. The human may also edit the description body or Executive Summary before push.

### Step 5: Push

**First push (multi-step: create JPD with placeholder → create sidecar → edit JPD with sidecar URL → transition + frontmatter):**

**Step 5a — Create JPD issue with `<<SIDECAR_URL>>` placeholder:**

The description body built in Step 3 still contains the literal `<<SIDECAR_URL>>` token in the Research Summary's "Full development research:" link line. Submit it as-is — the placeholder gets replaced in Step 5c after the sidecar exists.

Call `mcp__atlassian__createJiraIssue` with:

- `cloudId`: Cloud ID from `jira-config.md > Connection`
- `projectKey`: project key from `jira-config.md > Connection`
- `issueTypeName`: `Idea`
- `summary`: the prepared summary
- `description`: the prepared description body (still contains `<<SIDECAR_URL>>`)
- `additional_fields`: object containing all custom fields:
  - All static fields from `jira-config.md > Static Field Values` (field IDs and option IDs as specified there)
  - Executive Summary field ID and format from `jira-config.md > Dynamic Field Mappings`: string value
  - Domain Objective field ID from `jira-config.md > Dynamic Field Mappings`, option ID from `jira-config.md > Domain Objective Mapping`: multi-checkbox array
  - AI Feature field ID from `jira-config.md > Dynamic Field Mappings`: `1` (numeric, omit if not applicable)
  - `labels`: themes array (e.g., `["ai-capabilities"]`)

Extract `jira-key` from the response. Build `jira-url` as `{Atlassian base URL from jira-config.md}/browse/{jira-key}`.

**Step 5b — Create the sidecar folder:**

Build the folder name: `{jira-key} - {sanitized-idea-title}`. Sanitize the idea title by replacing forward slashes (`/`) with hyphens (`-`); preserve other characters including Unicode. Example: `PROJ-123 - Cache Route Optimization`.

Submit to `mcp__claude_ai_Google_Drive__create_file`:

- `title`: the sanitized folder name
- `parentId`: `incubator.jpd_sidecars_folder_id` from CLAUDE.md
- `contentMimeType`: `application/vnd.google-apps.folder`
(no `textContent` — folders have no content)

Capture `id` and `viewUrl` from the response. The `viewUrl` is the `sidecar-folder-url` (used in Step 5d). The `id` is the folder ID (used as `parentId` for each file in Step 5c).

**Step 5c — Create the four sidecar `.md` files in parallel:**

For each of the four staged files from Step 3c, substitute the literal frontmatter placeholders:

- Replace `<<JIRA_KEY>>` with `{jira-key}`
- Replace `<<JIRA_URL>>` with `{jira-url}` (built as `{Atlassian base URL}/browse/{jira-key}`)

Then submit four parallel `mcp__claude_ai_Google_Drive__create_file` calls — one per stream:

```text
For each (filename, stream-slug, content):
  create_file:
    title: {filename}                              # e.g. "EdTech Market Analysis.md"
    parentId: {sidecar-folder-id from Step 5b}
    textContent: {full substituted markdown including frontmatter}
    contentMimeType: text/markdown
```

The `text/markdown` content uploads as a raw `.md` file (not auto-converted to a Google Doc). This is by design — the sidecar architecture treats `.md` as the canonical format. Drive's preview pane renders the markdown as readable text; readers who want a styled Doc can right-click → Open with → Google Docs (per-account markdown preference must be enabled — see Google's [July 2024 markdown import announcement](https://workspaceupdates.googleblog.com/2024/07/import-and-export-markdown-in-google-docs.html)).

If any file create fails, note the failure and continue — partial sidecar is better than rolled-back. Surface the failure list in Step 6's success report.

**Step 5d — Edit JPD issue to substitute the sidecar folder URL:**

Call `mcp__atlassian__editJiraIssue` with:

- `cloudId`: Cloud ID from `jira-config.md > Connection`
- `issueIdOrKey`: `{jira-key}` from Step 5a
- `fields`: object with `description` set to the description body where every occurrence of `<<SIDECAR_URL>>` has been replaced with `{sidecar-folder-url}` (the placeholder appears twice — Research Summary trailer and Disruptive Reframing trailer; both must be substituted). The folder URL is the canonical sidecar reference, NOT a per-file URL.

Description-only edit — all other fields stay as set in Step 5a.

**Step 5e — Transition and update local frontmatter:**

Transition the issue to "1 - Opportunity Identification" using `mcp__atlassian__transitionJiraIssue` with the transition ID from `jira-config.md > Transition`. This moves the issue from the default "Backlog" status into the proper workflow state.

Update the idea file frontmatter via `mcp__obsidian__update_frontmatter` (the vault redirect hook blocks generic Edit on vault `.md` files):

- Add or update `jira-key: {jira-key}`
- Add or update `jira-pushed-at: {today's date YYYY-MM-DD}` — use `Bash(date:*)` to get today's date
- Add `jira-sidecar-url: {sidecar-folder-url}` (folder URL, not a single-file URL)

**Re-push (default — sidecar unchanged):**

The description body built in Step 3 uses `jira-sidecar-url` from idea frontmatter substituted directly into the Research Summary "Full development research:" link line — no `<<SIDECAR_URL>>` placeholder, no Drive call, no second editJiraIssue. Just one editJiraIssue.

Call `mcp__atlassian__editJiraIssue` with:

- `cloudId`: Cloud ID from `jira-config.md > Connection`
- `issueIdOrKey`: the existing `jira-key` from frontmatter
- `fields`: object containing fields being updated (`summary`, `description`, `labels`, plus any custom field changes — same structure as Step 5a's `additional_fields`)

Before pushing, show a diff of what changed since the last push (compare current payload to what was previously pushed — if this is the first re-push and no prior payload is stored, note "First re-push — showing full payload").

Update `jira-pushed-at` in frontmatter via `mcp__obsidian__update_frontmatter`. Do NOT change `jira-sidecar-url` — the existing sidecar is unchanged.

**Re-push with sidecar correction (in-place):**

Use this path when sidecar content needs fixing — corrected `incubator.research_db_label`, regenerated research artifact, typo, etc. The folder URL stays canonical; only the affected files are touched. JPD link, frontmatter `jira-sidecar-url`, and any sidecar files that don't need correction all stay untouched.

Drive MCP exposes no edit-in-place or delete tool. The human deletes the affected files via the Drive UI; this skill recreates them in the same folder with corrected content.

1. **Identify which files need correction.** Be specific — only those files get touched. Common cases: 1-3 files for a label or wording fix; 1 file for a regenerated artifact.
2. **Stage corrected content** for those files per Step 3c — substitute `<<JIRA_KEY>>`, `<<JIRA_URL>>`, and `<<RESEARCH_DB_REF>>` directly using the known `jira-key` and `incubator.research_db_label` (no placeholders needed since values are known).
3. **Ask the human to delete** the affected files from the existing sidecar folder via the Drive UI. Provide the folder URL from frontmatter `jira-sidecar-url` and the exact filenames so they don't have to navigate or guess. Wait for confirmation before proceeding.
4. **Recreate the corrected files** via `mcp__claude_ai_Google_Drive__create_file` with `parentId` = the existing sidecar folder ID. Derive the folder ID from frontmatter `jira-sidecar-url` (last path segment) or via `mcp__claude_ai_Google_Drive__search_files` if the URL form is opaque.
5. **No JPD edit.** Description body still points at the same folder URL.
6. **No frontmatter update.** `jira-sidecar-url` is unchanged. `jira-pushed-at` only updates if the JPD description body itself is also being re-pushed in the same invocation; for sidecar-only correction it stays.

If sidecar correction is the entire scope of the invocation (no card content changes, no JPD field changes), skip Step 4 (Human Review Gate) for the JPD payload — there is no payload changing. The delete-and-confirm exchange in step 3 above is the human gate for this path.

### Step 6: Report

```text
Push successful: {idea-name}

**JPD Issue:** {issue-key}
**URL:** {Atlassian base URL from jira-config.md}/browse/{issue-key}

**Research Sidecar Folder:** {sidecar-folder-url}
- {N} files created (of 4 expected): {comma-separated filenames; flag any missing as "skipped — {artifact} not present"}
{On re-push (no sidecar correction): "Sidecar unchanged: {jira-sidecar-url from frontmatter}"}
{On in-place sidecar correction: "Sidecar files corrected: {comma-separated filenames}; folder URL unchanged: {jira-sidecar-url from frontmatter}"}

Local frontmatter updated:
- jira-key: {issue-key} (only on first push)
- jira-pushed-at: {date} (omit on sidecar-only correction)
- jira-sidecar-url: {sidecar-folder-url, only on first push}
```

## Re-push Guidance

**Re-push warranted when:**

- Strategic direction shifts
- Impact dimensions change significantly
- Human explicitly requests

**Re-push NOT warranted when:**

- Output doc gains detail (that's Stage 3+ work, separate from the card)
- Minor wording refinements

## Error Handling

| Condition | Behavior |
| ----------- | ---------- |
| No argument and no eligible ideas | Report "No developing-or-later ideas found" and exit |
| Idea file not found | Report with available filenames, exit |
| Idea at seed stage | Report "Idea is at seed stage — develop it first with /develop" and exit |
| Missing impact dimensions | Report which dimensions are null, exit |
| Missing TL;DR sections | Report which sections are incomplete, exit |
| Atlassian API error on create | Report the error. Do not update frontmatter. Exit. |
| Atlassian API error on edit | Report the error. Do not update frontmatter. Exit. |
| Human declines at review gate | Exit without pushing |

## Scope Boundaries

This skill does NOT:

- Develop ideas (that's `/develop`)
- Draft output documents (that's `/draft`)
- Sync back from JPD (sync-back is conversational and ad-hoc)
- Push seeds (must be developing or later)
- Push without human review
- Modify the idea card body, with two exceptions — the Step 3a self-heal fallback may insert a `### Cross-Domain Signals` section if it's missing from the card and the artifact exists, and the Step 3b self-heal fallback may insert a `### Disruptive Reframing` section if it's missing from the card and the divergent-angles artifact exists (both architecture migration handling). All other body content is left untouched. Frontmatter updates remain limited to `jira-key`, `jira-pushed-at`, and `jira-sidecar-url`.
- Manage initiative hierarchy in JPD (initiatives are local only)
