---
name: competitive-landscape
description: "Competitive intelligence skill over the Snowflake-backed research database — query, research, and capture competitor findings for the configured domain. Explicit invocation only."
context: fork
agent: competitive-landscape
disable-model-invocation: true
allowed-tools: ["Bash", "WebSearch", "WebFetch", "Read", "Grep", "Glob", "SendMessage", "ToolSearch"]
---

# /competitive-landscape — Competitive Intelligence Skill

Two-layer interface over the Snowflake-backed research database (`scripts/research-db.py`): a small set of command patterns (query, research, capture) the skill routes to, and a translation layer that converts a natural-language ask into the matching pattern. Explicit invocation only for v1 — no auto-detection triggers fire this skill; a caller must invoke it directly.

**Platform constraint (GitHub #49559):** `context: fork` + `agent:` is not currently honored by the platform — the two together don't reliably launch the linked agent yet. Until that's fixed, invoke the `competitive-landscape` agent directly (a normal agent spawn) rather than relying on this skill's `context: fork` wiring to do it. This file still carries the procedure the direct spawn should follow, and the frontmatter linkage documents the intended wiring for when the platform catches up — it is not a currently-functioning auto-route, and tool scoping on the skill invocation path should not be assumed until the fix lands (the agent file's own `tools:` declaration is the scoping that's actually enforced today).

## Command Patterns

Three things a caller can ask for. The translation layer below maps a natural-language ask to one of these.

| Pattern | Playbook | What it does |
| --- | --- | --- |
| **query** | `playbooks/query.md` | Read-only. Answers a question against the database — a single-entity lookup or a cross-row relationship question. Absorbs what would otherwise be a separate "analyze" mode: the discriminator inside `query.md` decides which shape the question is and routes accordingly. Never writes. |
| **research** | `playbooks/research.md` | Web + database. Investigates a topic, stages candidate findings for the operator's write approval. |
| **capture** | `playbooks/capture.md` | Direct-write path for intel a human hands the agent (not agent-discovered). Shares the write-gate with research but the provenance label differs — capture items are never labeled discovered. |

`playbooks/write-gate.md` is cross-cutting — see § Loading below for which parts apply to which pattern.

**Discriminator test (verbatim):** the `query` pattern's internal split between a simple lookup and a relationship question is decided by this exact test:

> Would a correct answer contain any sentence whose truth rests on a relationship between rows, rather than on the content of one row? Yes → analyze. No → query.

In this skill's collapsed command-pattern model, "analyze" is not a separate top-level pattern — "Yes" routes to the relationship-question branch inside `playbooks/query.md`; "No" routes to that same file's simple-lookup branch. See `playbooks/query.md` for the full routing logic built on this test.

## Translation Layer

Given a natural-language ask, resolve to one pattern before doing anything else:

1. **Does the ask supply a specific claim to persist, sourced from a human** ("X told me Y," "log this," "I heard that...")? → **capture**.
2. **Does answering require finding NEW information** the database doesn't already have (web research, a topic with no existing findings)? → **research**.
3. **Otherwise** — answerable from what's already in the database → **query**. `query.md`'s own discriminator further splits this into a simple lookup vs. a relationship question; that split is internal to the query playbook, not part of this top-level routing.

If an ask is ambiguous between capture and research (a human reports something AND asks the agent to dig further), treat it as **research** — its protocol already handles a human-sourced starting point, and `write-gate.md`'s provenance labeling is what keeps agent-discovered and human-provided claims distinct within a single pass, not a separate command pattern.

## Loading

Load the playbook for the resolved pattern, plus `write-gate.md` always:

- **`write-gate.md` § Insufficiency & Degradation** applies to every pattern, including `query` — a query that can't be answered still needs the insufficiency affordance, and any pattern can hit a CLI/auth failure.
- **`write-gate.md` § Write Protocol** (environment wall, model-layer curation, provenance boundary, facts-immutable, force-flag refusal) applies only when `research` or `capture` actually reaches a write decision. `query` never writes, so this section never governs a `query` turn.

## Explicit Invocation Only (v1)

This skill does not auto-trigger on natural language (`disable-model-invocation: true`). A caller must invoke it directly — a `/competitive-landscape <ask>` slash invocation, or (per the platform-constraint note above) a direct spawn of the `competitive-landscape` agent. No auto-detection triggers exist in this version; that's a deliberate v1 scoping choice, not an oversight.
