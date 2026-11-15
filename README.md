# Incubator

A Claude Code pipeline that takes a raw product idea through automated research — competitive landscape, market sizing, domain read, and a reframing pass — drafts the strategy doc or product brief, and adversarially stress-tests strategic positions when the decision carries weight. Research streams run as parallel background agents; a Snowflake research database enforces write-validation; independent critics — a curation-fidelity skeptic, an artifact critic, and a named attack palette for thesis testing — run in isolated contexts, orchestrated through Claude Code skills.

## Installation

Clone the repo, then set up the Claude Code directory:

```text
mv claude .claude
```

Ideas, research, output documents and your configuration live in Notion, so the pipeline needs the Notion connector. Create an Ideas, a Research and an Outputs database and a Configuration page, and name their URLs in the front matter of `CLAUDE.md` (`notion_ideas`, `notion_research`, `notion_outputs`, `notion_config`). Put the keys from `.claude/instance.sample.md` on the Configuration page, in one `yaml` block, and fill in your own values. `reference/skill-conventions-notion-access.md` lists the fields the databases need.

### Required configuration

| Field | Location | What to set |
| --- | --- | --- |
| `role` | Configuration page | Your title and domain, e.g. "Head of Product Design (Coursebook)" |
| `persona_skill` | Configuration page | Name of the skill holding your own voice and writing style guide |
| `example_card` | Configuration page | URL of a Notion page holding an example developed card (start from `Examples/developing-card.sample.md`) |
| `strategic_context.product_strategy` | Configuration page | Path and URL to your product strategy document |
| `strategic_context.design_strategy` | Configuration page | Path and URL to your design strategy document |
| `strategic_context.okrs` | Configuration page | Path to your OKRs / organizational goals |
| `approach` | Configuration page | URL of a Notion page holding your drafting methodology — the structure and quality bar for strategy docs and briefs. Loaded by `/draft` and `/refine`; the core pipeline runs without it |
| `template_strategy_doc`, `template_product_brief`, `template_review` | Configuration page | URLs of the Notion pages holding your output and review templates (start from the samples in `Templates/`) |

### Optional configuration

| Field | Location | What to set |
| --- | --- | --- |
| `metrics.nps_product_a`, `metrics.nps_product_b` | Configuration page | Paths to NPS analysis directories for your products |
| `jira.*` | Configuration page | Your Atlassian cloud ID, project key, field IDs, and option IDs for JPD integration |
| `cross_domain.org_reference` | Configuration page | URL of a Notion page with your org's product brands, domains, and squads for cross-domain discovery (start from `plugins/incubator/skills/cross-domain/org-taxonomy.sample.md`) |
| `scripts/research-db-config.json` | Scripts directory | Copy from `research-db-config.sample.json`, fill in your database connection details for the research database integration (see below) |
| `incubator.learning_outcome_break_condition` | Configuration page | Your product-anchored break condition, tested against every thesis in `/thesis-test` — see `.claude/instance.sample.md` for the shape |

## What's Included

### Core pipeline

Stage transitions — the main path an idea takes from raw seed to finished document.

| Artifact | Type | What it does |
| --- | --- | --- |
| `/refine-seed` | Skill | Interprets a raw seed's intent, drafts header fields, classifies capability-vs-experience framing, surfaces related ideas, and aligns with you before development |
| `/develop` | Skill | Orchestrates research across five streams — internal strategy context (orchestrator), competitive positioning (edtech-sme), market sizing (tam-estimate), educator perspective (educator-sme), divergent reframing (divergent-thinking), and cross-domain discovery — with the four research agents running in parallel, a skeptic auditing handoff fidelity before synthesis, and a mechanical spine check that flags rubber-stamped seeds in the final verdict (Stage 1 to 2) |
| `/develop-synthesis` | Skill + Agent | Strategic synthesis engine dispatched by `/develop` — transforms a seed + research handoff into a TL;DR card with opportunity assessment, research summary, and thought outline (runs on Opus) |
| `/draft` | Skill | Creates a first template-aligned output document (strategy doc or product brief) from a developed idea card (Stage 2 to 3) |
| `/refine` | Skill | Iteratively refines an output document through section-by-section collaboration, voice alignment, and strategic realism checks (Stage 3 to 4 to 5) |

### Utilities

| Artifact | Type | What it does |
| --- | --- | --- |
| `/revert-to-seed` | Skill | Reverts a developing-stage card to seed stage for re-development — preserves identity fields and Original Capture, moves the idea's research rows to Notion's trash, and runs `/refine-seed` with the developed header fields as autonomous direction confirmation |

### Enrichment

Add research artifacts to an idea without changing its stage. Invokable standalone or called by `/develop` during orchestration.

| Artifact | Type | What it does |
| --- | --- | --- |
| `/cross-domain` | Skill | Queries your JPD project for ideas from other product domains with functional overlap |
| `/edtech-sme` | Skill + Agent | Evaluates an idea against edtech market dynamics, competitive landscape, buyer behavior, and technology trends |
| `/educator-sme` | Skill + Agent | Evaluates an idea through the lens of a veteran educator focused on pedagogical practice, classroom reality, and adoption likelihood |
| `/tam-estimate` | Skill + Agent | Produces defensible TAM/SAM/SOM estimates using top-down and bottom-up methodologies |
| `/divergent-thinking` | Skill + Agent | Generates 3-5 unexpected, nonlinear connections by following structural pattern similarity across domains |
| `/buildable-surface` | Skill + Agent | Detects principle-shaped ideas and generates distinct product approach candidates; no-ops on feature-shaped ideas |

### Adversarial testing

| Artifact | Type | What it does |
| --- | --- | --- |
| `/thesis-test` | Skill | Stress-tests 2–5 rival strategic positions against per-lens break conditions — generated by "what would have to be true" fragility ranking plus a named attack palette (`attack-patterns.md`) — then synthesizes stack-rank, component recomposition, conditions-for-survivor, premortem, and dated retest signposts. Card-mode and arbitrary-subject mode |
| `/skeptic` | Skill + Agent | Fresh-context evidence auditor with two modes: handoff fidelity (did curation drop counter-signals — runs inside `/develop` before synthesis) and card decay (do a card's claims still hold against current reality — ad hoc, reads signposts first) |

### Quality

| Artifact | Type | What it does |
| --- | --- | --- |
| `artifact-critic` | Agent | Checks TL;DR cards and output documents for structural conformance, voice conformance, and rating calibration in a fresh forked context; loads a bundled thesis-verdict rubric when auditing thesis-test artifacts |

### Publishing

| Artifact | Type | What it does |
| --- | --- | --- |
| `/jpd-push` | Skill | Pushes a developed idea to Jira Product Discovery for stakeholder visibility, with re-push support |

### Research database (optional)

An optional Snowflake database provides the structured competitive intelligence and customer evidence that the enrichment skills query and write back to. The database gives enrichment agents a head start (what's already known about competitors), enables mid-research deep-dives (query the database when web research surfaces a known competitor), and receives write-back of durable findings for future runs.

| Artifact | Type | What it does |
| --- | --- | --- |
| `scripts/research-db.py` | Utility | Database access layer — SQL generation, 9 commands for query, write, upsert, and gap detection |
| `scripts/research-db-config.sample.json` | Config template | Connection details for your Snowflake account |
| `scripts/schema/ddl-snowflake.sql` | Schema | Snowflake DDL for the strategy research schema (5 tables, 1 view) |

Without the database, skills work normally — they fall back to web searches. No core functionality is lost; the database is additive.

### Reference documents

| File | What it does |
| --- | --- |
| `incubator-reference.md` | Thin section index mapping each topic to a file under `reference/` — loaded on demand so skills pull one section, not the whole doc |
| `reference/` | Section-scoped reference files (stage model, two-track architecture, frontmatter schema, templates, workflow, research protocol, shared research, initiative schema, JPD integration, skill conventions) |
| `Templates/strategy-document-template.sample.md` | Sample output template for strategy documents — yours goes on a Notion page |
| `Templates/product-brief-template-v2.sample.md` | Sample output template for product briefs — yours goes on a Notion page |

## Configuration

The system separates what you configure from what skills handle.

**You configure:**

- The Configuration page in Notion -- your role, paths to external strategy documents, OKRs, NPS directories, and your Atlassian connection details (optional, for JPD integration)
- Your persona skill -- your writing voice and style
- Your template and approach pages in Notion -- your organization's output document conventions

**Skills handle:**

- Stage transitions and frontmatter updates
- Research orchestration (strategy doc queries, web search, cross-domain discovery)
- Opportunity assessment with calibrated rubrics
- Artifact generation following your templates and voice
- JPD push formatting and field mapping

See `.claude/instance.sample.md` for the full configuration contract with placeholder values.

## Usage

### Running: core pipeline

The pipeline runs left to right: capture (external), then refine-seed, develop, draft, refine.

```text
/refine-seed foraging-intelligence
```

Interprets the seed, drafts structured fields, surfaces related ideas, presents for your alignment.

```text
/develop foraging-intelligence
```

Researches and synthesizes into a TL;DR card with opportunity assessment and impact dimensions.

```text
/draft foraging-intelligence
```

Prompts for output format (strategy doc or product brief), creates a first draft as a row in the Outputs database.

```text
/refine foraging-intelligence
```

Iterates on the output document section-by-section until you approve it as complete.

### Running: enrichment

Run independently at any time to add research without changing stage:

```text
/edtech-sme foraging-intelligence
/educator-sme foraging-intelligence
/tam-estimate foraging-intelligence
/cross-domain foraging-intelligence
/divergent-thinking foraging-intelligence
/buildable-surface foraging-intelligence
```

### Running: adversarial testing

Stress-test a developed card whose direction is contested, or an arbitrary subject:

```text
/thesis-test foraging-intelligence
/thesis-test --subject "Foraging Intelligence platform vision" --brief path/to/brief.md
```

Audit whether a developed card's claims still hold months later:

```text
/skeptic foraging-intelligence
```

### Running: publishing

Push to Jira Product Discovery when the idea is mature:

```text
/jpd-push foraging-intelligence
```

## How It Works

Ideas move through five stages: **Seed** (raw capture with frontmatter), **Developing** (researched TL;DR card), **Drafting** (first output document), **Refining** (iterative collaboration), and **Complete** (human-approved).

The system uses a two-track architecture. Idea cards — rows in the Ideas database — progressively accumulate content through Stages 0-2 and serve as scannable, shareable artifacts. Output documents are separate rows in the Outputs database, created at Stage 3 and related to their idea card.

Custom agents handle specialized reasoning: `develop-synthesis` does the strategic judgment work, `artifact-critic` and the `skeptic` audit conformance and evidence fidelity from fresh contexts, and five domain-specific agents provide enrichment research — the research streams running as parallel background agents with all writes-of-record serialized by the orchestrator. When a decision is heavy — net-new territory, gnarly, or critical positioning tradeoffs — `/thesis-test` stress-tests rival positions adversarially; a mechanical spine check at the end of every `/develop` run flags when enrichment merely confirmed the seed.

Human decision authority is preserved at every meaningful gate. Seeds develop autonomously, but all stage transitions beyond Stage 1, output format decisions, and final approvals require human initiation or sign-off.

## Customization

The system ships with domain knowledge tuned for education technology and assessment products. To adapt it:

- **Different product domain:** Point `persona_skill` at a skill with your voice, update the agent personas in `plugins/incubator/agents/` (especially `edtech-sme.md`, `educator-sme.md`, `tam-estimate.md`) with your market's domain knowledge, and update the organizational taxonomy in `plugins/incubator/skills/cross-domain/`.
- **Different output formats:** Put your own templates and your own approach methodology on the Notion pages the `template_*` and `approach` keys name.
- **Without JPD integration:** Leave the `jira.*` keys unset. The `/jpd-push` and `/cross-domain` skills are self-contained and can be ignored.
- **Without the research database:** Skip `scripts/research-db-config.json` setup. Skills fall back to web searches and idea-scoped research artifacts. The database is additive.
- **Without enrichment agents:** Each enrichment agent is independently invokable. Remove any you don't need from `.claude/skills/` and `.claude/agents/` without affecting the core pipeline.

## Security

Review skills before installing. They load into Claude's context and execute with your permissions. Audit the contents of `.claude/skills/` and `.claude/agents/` before use.

## License

MIT. See [LICENSE](LICENSE).
