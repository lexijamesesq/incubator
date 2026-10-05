---
tags:
  - type/claude-repo
description: "Claude Code skills for a strategic-ideas incubation pipeline — draft, develop, refine, and thesis-test ideas with agent-based market/competitive enrichment."
docs_home: "{workspace_root}/Projects/Incubator"
---

# Incubator

A Claude Code pipeline for strategic idea development: `/draft`, `/develop`, `/refine`, `/thesis-test`, plus enrichment agents (edtech-sme, educator-sme, tam-estimate, competitive-landscape, skeptic, artifact-critic, divergent-thinking, buildable-surface) and supporting skills (`cross-domain`, `jpd-push`). Public repo: a template other design/product leaders fork and configure for their own domain, not just this operator's pipeline. Also the source for the confirmed-shared skill/agent subset (8 skills, 6 agents) published as the `incubator` plugin and consumed elsewhere (Strategy, professional profile only) at user scope — not a symlink.

## Setup

Clone the repo. `.claude/` ships tracked and committed — review its contents (see Security below) before opening the directory in Claude Code. Copy the instance config sample and fill in your own values:

```bash
cp .claude/instance.sample.md .claude/instance.md
cp jira-config.sample.md jira-config.md
cp persona.sample.md persona.md
```

See `.claude/instance.sample.md` for the full configuration contract (role, strategic-context paths, metrics paths, research-database label) with placeholder values.

## Configuration

Skills read instance-specific values from `.claude/instance.md`'s Configuration section by key name, not hardcoded — `role`, `strategic_context.*`, `metrics.*`, `incubator.research_db_label`, `incubator.learning_outcome_break_condition`. Product-specific org taxonomy lives in `plugins/incubator/skills/cross-domain/org-structural-reference.md` (copy from the sibling `.sample.md`). Jira connection details live in `jira-config.md`. All gitignored — every fork fills in its own.

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

- Skills are self-contained `SKILL.md` files under `.claude/skills/{name}/`, agents under `.claude/agents/{name}.md` — no shared runtime beyond the Configuration keys above.
- Instance-specific values are always config keys, never hardcoded — a skill that hardcodes a path/URL breaks for every other fork.
- `reference/` holds section-scoped reference docs (stage model, schemas, workflow, voice standards) that skills load on demand — indexed by `incubator-reference.md`.
- Commits: gitleaks-staged/-pre-push/-commit-msg (dotty's exported hooks) gate every commit and push locally; CI re-proves the outgoing PR range independently.
- This repo is a shared-skill source for other projects: a consumer project may symlink individual skills/agents in at project scope (interim — the durable resolution is a published plugin from this repo). A skill/agent rename or removal here can break a consumer; check before renaming.

## Key Files

| File | Purpose |
| ------ | --------- |
| `.claude/instance.sample.md` | Configuration contract template — copy to `.claude/instance.md` and fill in your instance's values |
| `.claude/skills/` | The pipeline skills: `draft`, `develop`, `refine`, `refine-seed`, `revert-to-seed`, `thesis-test`, `jpd-push`, `cross-domain`, `buildable-surface`, `develop-synthesis`, `competitive-landscape`, `artifact-critic`, `edtech-sme`, `educator-sme` |
| `.claude/agents/` | Enrichment agent personas invoked by the pipeline skills |
| `incubator-reference.md` | Thin index into `reference/` — read this first, not the individual reference files, unless a skill points at one directly |
| `reference/` | Section-scoped reference docs (stage model, schemas, workflow, voice/output standards) |
| `jira-config.sample.md`, `persona.sample.md` | Per-fork config templates — copy to the non-`.sample` name and fill in |
