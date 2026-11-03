# Strategy Incubator

## Reference Material

Reference material is split into section-scoped files under `reference/`, indexed by `incubator-reference.md`. Do NOT load the whole set — each pipeline skill names the specific `reference/{section}.md` file(s) it needs in its own "Reference Material" instruction. Consult `incubator-reference.md` only to find which section file maps to a topic (stage model, architecture, frontmatter schema, templates, workflow, research protocol, shared research, initiative schema, JPD integration, skill conventions).

All outputs from Stage 2 onward follow `persona.md`.

---

## Core Documents

**For any incubator work:**

1. This .claude/instance.md — configuration and project state
2. `persona.md` — Voice and style (applies Stage 2 onward)
3. `incubator-reference.md` — Thin section index -> `reference/` (stage model, architecture, schemas, templates, workflow, research protocol, shared research, initiative schema, JPD integration). Load only the section file(s) a task needs, not the whole set.

**For Stage 3+ drafting work:**
4. `incubator-approach.md` — Unified methodology (strategy docs and product briefs)
5. `Templates/strategy-document-template.md` — Strategy output template
6. `Templates/product-brief-template-v2.md` — Brief output template

**For strategic context (load targeted sections, not full files):**

- See Configuration > External References below for paths

---

## Session Preconditions

The pipeline depends on multiple MCP servers. Verify connections before invoking long-running skills (especially `/develop` and `/draft`) — partial-state failures mid-run waste both work and tokens.

| MCP Server | Used By | Failure Mode |
| --- | --- | --- |
| Obsidian | All skills that read/write vault `.md` files | Pipeline-wide failure — vault redirect hook blocks `Read`/`Edit`/`Write`/`Grep` and routes to Obsidian MCP. Without it, skills cannot read idea cards, NPS files, persona, strategy docs. |
| Atlassian | `/cross-domain` (read JPD), `/jpd-push` (write to JPD) | Skill-local failure with auth-flow recovery — surface the OAuth URL, retry once after user completes flow. |

**Recommended start-of-session check:** Run `/mcp` to surface connection state. If Obsidian or Atlassian shows disconnected, reconnect before invoking pipeline skills. Skills will fail noisily with auth instructions if MCP is missing, but a pre-flight check avoids interrupting a running pipeline mid-stream.

The optional research database is accessed via `python3 scripts/research-db.py`, not via MCP — separate auth path. See `scripts/research-db-config.sample.json` for setup.

---

## Configuration

### Role

The role skills act on behalf of. Referenced by /develop, /draft, and /refine.

```yaml
role: "YOUR_ROLE — e.g., Director of Product Design (Assessments)"
```

### External References

These paths point to files outside the Incubator project directory. Skills reference them by config key. Update these paths to match your environment.

```yaml
# Product strategy document (large file — skills use Grep, never full load)
strategic_context.product_strategy:
  path: "<your-product-strategy-document-path>"
  external_url: "<google-doc-or-external-url>"

# Design strategy document
strategic_context.design_strategy:
  path: "<your-design-strategy-document-path>"
  external_url: "<google-doc-or-external-url>"

# OKRs / organizational goals
strategic_context.okrs:
  path: "<your-okrs-document-path>"

# NPS or customer sentiment analysis directories (used by /develop).
# Each product has a local directory of monthly analysis files (one .md per month) AND a Google Doc
# that aggregates all months as separate tabs. Cite the external_url (with tab name in link text) when
# referencing NPS findings in research artifacts — internal docs/file paths should not appear as citations.
metrics.nps_product_a:
  path: "<path-to-nps-analysis-for-product-a>"
  external_url: "<google-doc-url-for-product-a>"
metrics.nps_product_b:
  path: "<path-to-nps-analysis-for-product-b>"
  external_url: "<google-doc-url-for-product-b>"

# Google Drive folder where /jpd-push generates Research Sidecar folders.
# Each pushed idea gets a sidecar folder containing the full research artifacts
# (TAM, EdTech, Educator, Divergent). Linked from the JPD body Research Summary
# and Disruptive Reframing trailers as `[Full development research](URL)`.
incubator.jpd_sidecars_folder_id: "YOUR_DRIVE_FOLDER_ID"
incubator.jpd_sidecars_folder_url: "YOUR_DRIVE_FOLDER_URL"

# Research database label used in /jpd-push sidecar `sources` blocks. Substituted into the
# <<RESEARCH_DB_REF>> placeholder at sidecar staging time, so the public skill template stays
# free of installation-specific identifiers while the generated sidecar files carry the
# concrete reference stakeholders need. Example: "Snowflake research database (YOUR_DB.YOUR_SCHEMA)".
incubator.research_db_label: "YOUR_RESEARCH_DATABASE_LABEL"

# Required learning-outcome break condition injected into every /thesis-test brief — the
# permanent per-thesis break condition tested by educator-sme's adversarial pass. Product-anchored:
# does the wedge land on a core-experience surface in your product, or only on a buyer pain through
# a procurement motion? The public /thesis-test skill and brief template carry only this config key;
# the real phrasing lives here and is pre-filled into each brief's learning-outcome row.
incubator.learning_outcome_break_condition: "TODO: your product-anchored break condition — does the wedge land on a core-experience surface in your product, or only on a buyer pain through a procurement motion?"
```

### JPD Integration (Optional)

If you use Jira Product Discovery for stakeholder visibility, copy `jira-config.sample.md` to `jira-config.md` and fill in your Atlassian cloud ID, project key, field IDs, and option IDs.

If you do not use JPD, the /jpd-push and /cross-domain skills can be safely ignored.

### Research Database Integration (Optional)

The /develop, /edtech-sme, and /educator-sme skills can optionally query a strategy research database (Snowflake or PostgreSQL) for structured competitive intelligence. The database augments the existing research pipeline — local shared research files and web research remain primary. The database provides a head start, enables mid-research deep-dives on known competitors, and receives write-back of durable findings for future runs.

To set up: copy `scripts/research-db-config.sample.json` to `scripts/research-db-config.json` and fill in your database connection details. Set the `RESEARCH_DB_BACKEND` environment variable to `snowflake` or `postgresql`.

If you do not set up the database, the skills work without it — they fall back to their pre-database research flow (local shared research files + web searches). No functionality is lost, but findings from previous runs won't carry over as structured intelligence.

---

## Customization Required

Before using this system, you must customize:

1. **`persona.md`** — Replace with your own voice and writing style guide. This governs how all output documents sound from Stage 2 onward.

2. **`.claude/instance.md` Configuration section** — Update all external reference paths to point to your actual strategy documents, OKRs, and NPS analysis directories.

3. **`Templates/`** — Review and adapt the strategy document and product brief templates to match your organization's conventions.

4. **`jira-config.md`** — Copy from `jira-config.sample.md` and fill in your Atlassian cloud ID, project key, field IDs, and option IDs if using JPD integration.

5. **`plugins/incubator/skills/cross-domain/org-structural-reference.md`** — Copy from `plugins/incubator/skills/cross-domain/org-taxonomy.sample.md` and fill in your organization's product brands, domains, and squads if using cross-domain discovery.

6. **Agent personas** — The edtech-sme, educator-sme, and tam-estimate agents carry domain knowledge specific to the education/assessment market. Adapt their domain knowledge sections if your product domain differs.

---

## Project State

**Last Updated:** YYYY-MM-DD

### Re-entry Cue
<!-- One sentence describing where things stand -->

### Current State
<!-- Bullet points on pipeline status, architecture, portfolio -->

### Next Actions (Max 5)

1. <!-- Action item -->

### Decisions Made (This Session)
<!-- Key decisions and rationale -->

---

## Intake

### Tasks

**Method:** Linear
**Project ID:** YOUR_PROJECT_UUID_HERE
**Location:** [Linear project: YOUR_PROJECT_NAME](YOUR_LINEAR_PROJECT_URL) (YOUR_TEAM team)
**Context:** Context/

### Narrative

**Method:** Linear Project Updates

### Notes

**Seed intake (Stage 0→1):** Items classified as strategy seeds by the inbox router are delivered here as seed files in `Ideas/`. Seeds require the full frontmatter schema and seed template defined in `incubator-reference.md` (sections: Frontmatter Schema, Seed Template). The router reads this contract and conforms — it does not carry its own copy of the schema.

**Signal-extracted seeds:** Ad-hoc captures with strategic signals also arrive as seeds via the same contract, with `source: slack`. Detection and extraction logic is the router's responsibility; the resulting file must conform to this project's seed contract.

**What the Incubator does NOT define:** Classification taxonomy, signal detection criteria, Origin Handoff Contract provenance rules, and processing order. Those are router responsibilities defined in your inbox processing system's router spec.
