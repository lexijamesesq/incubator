# Strategy Incubator

## Reference Material

Reference material is split into section-scoped files under `reference/`, indexed by `incubator-reference.md`. Do NOT load the whole set — each pipeline skill names the specific `reference/{section}.md` file(s) it needs in its own "Reference Material" instruction. Consult `incubator-reference.md` only to find which section file maps to a topic (stage model, architecture, frontmatter schema, templates, workflow, research protocol, shared research, initiative schema, JPD integration, skill conventions).

All outputs from Stage 2 onward follow the persona guide: the skill named by `persona_skill` below.

---

## Core Documents

**For any incubator work:**

1. The Configuration page — the keys below, on the page the instruction file's `notion_config` pointer names
2. The persona guide — the skill named by `persona_skill` — Voice and style (applies Stage 2 onward)
3. `incubator-reference.md` — Thin section index -> `reference/` (stage model, architecture, schemas, templates, workflow, research protocol, shared research, initiative schema, JPD integration). Load only the section file(s) a task needs, not the whole set.

**For Stage 3+ drafting work:**
4. The approach methodology — the Notion page `approach` names — Unified methodology (strategy docs and product briefs)
5. The strategy output template — the Notion page `template_strategy_doc` names
6. The brief output template — the Notion page `template_product_brief` names

**For strategic context (load targeted sections, not full files):**

- See Configuration > External References below for paths

---

## Session Preconditions

The pipeline depends on multiple MCP servers. Verify connections before invoking long-running skills (especially `/develop` and `/draft`) — partial-state failures mid-run waste both work and tokens.

| MCP Server | Used By | Failure Mode |
| --- | --- | --- |
| Atlassian | `/cross-domain` (read JPD), `/jpd-push` (write to JPD) | Skill-local failure with auth-flow recovery — surface the OAuth URL, retry once after user completes flow. |

**Recommended start-of-session check:** Run `/mcp` to surface connection state. If Atlassian shows disconnected, reconnect before invoking pipeline skills. Skills will fail noisily with auth instructions if MCP is missing, but a pre-flight check avoids interrupting a running pipeline mid-stream.

The optional research database is accessed via `python3 scripts/research-db.py`, not via MCP — separate auth path. See `scripts/research-db-config.sample.json` for setup.

---

## Configuration

The keys below are the configuration contract. Every skill reads them from a Configuration page (the page the instruction file's `notion_config` pointer names), which holds these same keys in one `yaml` block. This file is the public blank: real values go on the Configuration page, never in the repo, and no skill reads this file.

The instruction file (`CLAUDE.md`, front matter) carries four pointers beside this contract: `notion_ideas`, `notion_research` and `notion_outputs` (the URLs of the three databases — database URLs, not `collection://` data-source URLs) and `notion_config` (the URL of the Configuration page). `reference/skill-conventions-notion-access.md` states how skills use them.

### Role

The role skills act on behalf of. Referenced by /develop, /draft, and /refine.

```yaml
role: "YOUR_ROLE — e.g., Director of Product Design (Assessments)"
```

### Voice and Format Reference

`persona_skill` names the persona guide. A skill that loads the persona also accepts `persona_file=<path>` for a test run; a file that only points elsewhere is refused.

```yaml
# Name of the skill that supplies your voice and writing style, as the Skill tool loads it.
persona_skill: "YOUR_PERSONA_SKILL_NAME"

# URL of the Notion page holding your example developed card (the format reference for /develop-synthesis and /artifact-critic).
# Start from Examples/developing-card.sample.md.
example_card: "YOUR_EXAMPLE_CARD_PAGE_URL"

# URL of the Notion page holding your drafting methodology: the structure and quality bar for strategy
# documents and product briefs, with an "Output Format: Strategy Document" and an "Output Format: Product
# Brief" section. Read by /draft and /refine.
approach: "YOUR_APPROACH_PAGE_URL"

# URLs of the Notion pages holding your output templates and your stage review templates.
# Start from Templates/strategy-document-template.sample.md, Templates/product-brief-template-v2.sample.md
# and Templates/review-templates.sample.md. /draft reads all three; /refine reads template_review.
template_strategy_doc: "YOUR_STRATEGY_TEMPLATE_PAGE_URL"
template_product_brief: "YOUR_BRIEF_TEMPLATE_PAGE_URL"
template_review: "YOUR_REVIEW_TEMPLATES_PAGE_URL"
```

### External References

These paths point to local files outside the Incubator project directory: the strategy, OKR and NPS documents are not in Notion, and skills read them with Grep and Read. Skills reference them by config key. An absolute path is used as it is; a relative path resolves against `workspace_root` in your global Claude Code configuration. Update these paths to match your environment.

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

If you use Jira Product Discovery for stakeholder visibility, `/cross-domain` and `/jpd-push` read every Jira value from the keys below. A field's ID is given once, under `jira.fields`, and both skills take it from there.

```yaml
# Atlassian connection. Read by /cross-domain and /jpd-push.
jira.cloud_id: "YOUR_ATLASSIAN_CLOUD_ID"
jira.project_key: "YOUR_PROJECT_KEY"
jira.base_url: "https://YOUR_INSTANCE.atlassian.net"

# Field IDs, one key per field. /cross-domain reads the first five on every idea it retrieves.
# /jpd-push takes the ID of each field it sets from here: the static fields named in
# jira.static_values, and the three fields it derives from the card.
jira.fields.product_brand: "customfield_XXXXX"
jira.fields.product_domain: "customfield_XXXXX"
jira.fields.squad: "customfield_XXXXX"
jira.fields.product_surface_area: "customfield_XXXXX"
jira.fields.quarter_active: "customfield_XXXXX"
jira.fields.roadmap_priority: "customfield_XXXXX"
jira.fields.executive_summary: "customfield_XXXXX"
jira.fields.ai_feature: "customfield_XXXXX"
jira.fields.domain_objective: "customfield_XXXXX"

# The values /jpd-push sets the same on every push. One entry per static field, keyed by that
# field's name under jira.fields. `label` is the value as a person reads it; `value` is what is
# sent, in the format the field takes. Add or drop entries to match your tracker; an entry needs
# a jira.fields key of the same name.
jira.static_values:
  product_brand:
    label: "YOUR_BRAND"
    value: [{"id": "OPTION_ID"}]
  product_domain:
    label: "YOUR_DOMAIN"
    value: [{"id": "OPTION_ID"}]
  squad:
    label: "YOUR_SQUAD"
    value: [{"id": "OPTION_ID"}]
  product_surface_area:
    label: "YOUR_SURFACE_AREA"
    value: [{"id": "OPTION_ID"}]
  roadmap_priority:
    label: "YOUR_PRIORITY"
    value: [{"id": "OPTION_ID"}]
  quarter_active:
    label: "YOUR_DEFAULT_QUARTER"
    value: {"id": "OPTION_ID"}

# The objectives /jpd-push can select for the Domain Objective field, and when to select each.
jira.domain_objectives:
  - label: "Objective 1"
    option_id: "OPTION_ID"
    when: "Description of when to select"
  - label: "Objective 2"
    option_id: "OPTION_ID"
    when: "Description of when to select"

# The transition /jpd-push applies after creating an issue, and the name of the status it moves
# the issue to (e.g. out of the tracker's default status into your first workflow state).
jira.transition_id: "YOUR_TRANSITION_ID"
jira.transition_to_status: "YOUR_FIRST_WORKFLOW_STATUS"

# The Product Brand value that marks your own team's ideas; /cross-domain excludes them.
jira.own_brand: "YOUR_BRAND"

# Optional. URL of a Notion page describing your organization's product brands, domains, squads and
# surface areas, in the shape of plugins/incubator/skills/cross-domain/org-taxonomy.sample.md.
# Leave empty to run /cross-domain on JPD's own summaries and field values.
cross_domain.org_reference: ""
```

If you do not use JPD, the /jpd-push and /cross-domain skills can be safely ignored.

### Research Database Integration (Optional)

The /develop, /edtech-sme, and /educator-sme skills can optionally query a strategy research database (Snowflake) for structured competitive intelligence. The database augments the existing research pipeline — local shared research files and web research remain primary. The database provides a head start, enables mid-research deep-dives on known competitors, and receives write-back of durable findings for future runs.

To set up: copy `scripts/research-db-config.sample.json` to `scripts/research-db-config.json` and fill in your database connection details.

If you do not set up the database, the skills work without it — they fall back to their pre-database research flow (local shared research files + web searches). No functionality is lost, but findings from previous runs won't carry over as structured intelligence.

---

## Customization Required

Before using this system, you must customize:

1. **The persona** — A skill holding your own voice and writing style guide, named in `persona_skill`. This governs how all output documents sound from Stage 2 onward.

2. **The Notion databases and Configuration page** — An Ideas, a Research and an Outputs database, and a Configuration page holding the keys above in one `yaml` block; name their URLs in the `CLAUDE.md` front matter. Update all external reference paths to point to your actual strategy documents, OKRs, and NPS analysis directories. The Research database's `Research type` field needs these options: `edtech-market-analysis`, `tam-estimate`, `educator-sme-evaluation`, `divergent-angles`, `cross-domain-signals`, `synthesis-handoff`, `development-research`, `thesis-brief`, `thesis-test-partition`, `thesis-test-lens`, `thesis-test-synthesis`, `falsification-record`; its `Agent` field needs `edtech-sme`, `divergent-thinking`, `cross-domain`, `orchestrator`; its `Confidence` field `high`, `medium`, `low`; its `Domain calibration` field `k12`, `higher-ed`, `both`, `platform-downstream`. The Outputs database needs `Name`, `Idea`, `Format` (`strategy-doc`, `product-brief`), `Stage`, `Created` and `Updated`. `reference/skill-conventions-notion-access.md` lists the fields of the idea row.

3. **Templates and approach** — Put your strategy document, product brief and review templates (start from the samples in `Templates/`) and your drafting methodology on Notion pages, and name them in `template_strategy_doc`, `template_product_brief`, `template_review` and `approach`.

4. **Jira values** — The `jira.*` keys above, for `/cross-domain` and `/jpd-push`, if using JPD integration.

5. **The organizational reference (optional)** — A Notion page with your organization's product brands, domains, and squads, started from `plugins/incubator/skills/cross-domain/org-taxonomy.sample.md` and named in `cross_domain.org_reference`, if using cross-domain discovery.

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

**Seed intake (Stage 0→1):** Items classified as strategy seeds by the inbox router are delivered here as seed rows in the Ideas database. Seeds require the full frontmatter schema (as the row's fields) and seed template defined in `incubator-reference.md` (sections: Frontmatter Schema, Seed Template). The router reads this contract and conforms — it does not carry its own copy of the schema.

**Signal-extracted seeds:** Ad-hoc captures with strategic signals also arrive as seeds via the same contract, with `source: slack`. Detection and extraction logic is the router's responsibility; the resulting row must conform to this project's seed contract.

**What the Incubator does NOT define:** Classification taxonomy, signal detection criteria, Origin Handoff Contract provenance rules, and processing order. Those are router responsibilities defined in your inbox processing system's router spec.
