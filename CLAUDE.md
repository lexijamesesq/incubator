---
tags:
  - type/claude-repo
description: "Claude Code skills for a strategic-ideas incubation pipeline — draft, develop, refine, and thesis-test ideas with agent-based market/competitive enrichment."
linear_project_id: "59a883ba-891d-4740-b463-507f30752319"
linear_url: "https://linear.app/lexijamesesq/project/incubator-36f179a95864"
notion_project: "https://app.notion.com/p/4175f53f7dbc81d39f7bd6356e2d3f2b"
notion_knowledge: "collection://4185f53f-7dbc-815f-9a2b-000b54a0033e"
notion_ideas: "https://app.notion.com/p/4185f53f7dbc816aaf74f91467b08fde"
notion_research: "https://app.notion.com/p/4185f53f7dbc810898dbd357b8eeac32"
notion_outputs: "https://app.notion.com/p/4185f53f7dbc817d9e4effcdfd6f2d4d"
notion_config: "https://app.notion.com/p/4195f53f7dbc81f5b7fbd5980ba3276b"
---

# Incubator

A Claude Code pipeline for strategic idea development: `/draft`, `/develop`, `/refine`, `/thesis-test`, plus enrichment agents (edtech-sme, educator-sme, tam-estimate, competitive-landscape, skeptic, artifact-critic, divergent-thinking, buildable-surface) and supporting skills (`cross-domain`, `jpd-push`). Public repo: a template other design/product leaders fork and configure for their own domain, not just this operator's pipeline. Also the source for the confirmed-shared skill/agent subset (8 skills, 6 agents) published as the `incubator` plugin and consumed elsewhere (Strategy, professional profile only) at user scope — not a symlink.

The maintainer's own project documentation is in Notion and its work is tracked in Linear; the front matter above points to both. They are private: a fork has no access to them and does not need it.

## Setup

Clone the repo. `.claude/` ships tracked and committed — review its contents (see Security below) before opening the directory in Claude Code.

Ideas, research, outputs and the instance's configuration live in Notion. Create an Ideas, a Research and an Outputs database and a Configuration page, and name their URLs in this file's front matter (`notion_ideas`, `notion_research`, `notion_outputs`, `notion_config`). Put the keys from `.claude/instance.sample.md` on the Configuration page, in one `yaml` block, with your own values: that file is the full configuration contract (role, persona skill, example card, approach and template pages, strategic-context paths, metrics paths, Jira values, research-database label) with placeholders.

## Configuration

The front matter's four `notion_*` pointers are where the skills find everything: `notion_ideas`, `notion_research` and `notion_outputs` are the URLs of the three databases (database URLs, not `collection://` data-source URLs), and `notion_config` is the URL of the Configuration page. Every skill takes them from here and accepts each as a `key=value` argument override, which is how a test run is pointed at scratch databases. `reference/skill-conventions-notion-access.md` states the mechanics.

Skills read instance-specific values from the Configuration page's `yaml` block by key name, never hardcoded — `role`, `persona_skill`, `example_card`, `approach`, `template_strategy_doc`, `template_product_brief`, `template_review`, `strategic_context.*`, `metrics.*`, `jira.*`, `cross_domain.org_reference`, `incubator.jpd_sidecars_folder_id`, `incubator.research_db_label`, `incubator.learning_outcome_break_condition`. The persona is the skill `persona_skill` names. The approach methodology, the output and review templates and the example card are Notion pages those keys name. The strategy, OKR and NPS documents stay local files at the paths the `strategic_context.*` and `metrics.*` keys give. `.claude/instance.sample.md` is the public blank of the same keys; the page itself is private, and every fork fills in its own.

## Build / Test

No build step (skills are markdown; the one script is stdlib-first Python). Local checks before pushing:

```bash
uvx ruff@latest check .     # scripts/research-db.py
shellcheck **/*.sh          # if any shell scripts are added
pre-commit run --all-files  # gitleaks-staged + the standard hook set
```

## CI

`.github/workflows/ci.yml`, required via the "Protect main" ruleset: the estate's shared `floor` job (`ci / checks`) — its pre-commit suite runs ruff and shellcheck on the files a PR changes, except on a PR the triage step classifies as `mechanical` (`estate-ci.yml`'s own gate: `steps.triage.outputs.classification != 'mechanical'`, which the pre-commit step inherits via the `precommit_cfg` step it depends on) — so this repo carries no separate `ruff`/`shellcheck` job. PR-time secret scanning is the trusted lane's `trusted-scan` (`gate.yml`, dotty's shared `setup-gitleaks` composite action, base rules only + `--redact` — public repo, the operator's PII ruleset never reaches CI), a separate required check from a separate workflow (`pull_request_target`, not `ci.yml`).

## Conventions

- Skills are self-contained `SKILL.md` files under `.claude/skills/{name}/` or `plugins/incubator/skills/{name}/`, agents under the matching `agents/` directory — no shared runtime beyond the Configuration keys and the Notion conventions above.
- Instance-specific values are always config keys, never hardcoded — a skill that hardcodes a path/URL breaks for every other fork.
- `reference/` holds section-scoped reference docs (stage model, schemas, workflow, voice standards) that skills load on demand — indexed by `incubator-reference.md`.
- Commits: gitleaks-staged/-pre-push/-commit-msg (dotty's exported hooks) gate every commit and push locally; CI re-proves the outgoing PR range independently.
- This repo is a shared-skill source for other projects: a consumer project may symlink individual skills/agents in at project scope (interim — the durable resolution is a published plugin from this repo). A skill/agent rename or removal here can break a consumer; check before renaming.

## Key Files

| File | Purpose |
| ------ | --------- |
| `.claude/instance.sample.md` | Configuration contract template — the public blank of the Configuration page's keys. Put the keys on your Configuration page |
| `.claude/skills/` | The pipeline skills kept in this repo only: `draft`, `develop`, `refine`, `refine-seed`, `revert-to-seed`, `jpd-push`, `buildable-surface`, `develop-synthesis`, `competitive-landscape` |
| `plugins/incubator/skills/` | The shared skills published as the `incubator` plugin: `thesis-test`, `cross-domain`, `artifact-critic`, `edtech-sme`, `educator-sme`, `tam-estimate`, `divergent-thinking`, `skeptic` |
| `.claude/agents/`, `plugins/incubator/agents/` | Agent personas invoked by the pipeline skills |
| `reference/skill-conventions-notion-access.md` | How a skill reaches ideas, research rows, configuration and the persona in Notion — the one statement of the shared mechanics |
| `incubator-reference.md` | Thin index into `reference/` — read this first, not the individual reference files, unless a skill points at one directly |
| `reference/` | Section-scoped reference docs (stage model, schemas, workflow, voice/output standards) |
