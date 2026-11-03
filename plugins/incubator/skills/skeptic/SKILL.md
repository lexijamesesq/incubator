---
name: skeptic
description: This skill should be used when the user asks to "run the skeptic on [idea]", "is [idea] still credible", "skeptic check [idea]", or "audit [idea] against current reality". Launches the skeptic agent to audit a developed idea card's load-bearing claims (card-decay), or a /develop run's handoff fidelity when pointed at a run in progress. Reports the verdict; never modifies the card.
argument-hint: [idea-name]
context: conversation
disable-model-invocation: false
allowed-tools:
  - Glob
  - Grep
  - mcp__obsidian__read_note
  - mcp__obsidian__list_directory
  - Agent
---

# /skeptic — Ad-Hoc Evidence Audit

The human's verb for the skeptic agent. Audits whether a developed idea's evidence is still standing — did it decay against current reality, or (when pointed at a run in progress) did the /develop handoff survive compression. Reports only; the card is never modified.

## Invocation

```text
/skeptic [idea-name]
```

## Execution

1. **Resolve the idea.** Exact match at `Ideas/{arg}.md` (strip `.md` first); else case-insensitive substring match across `Ideas/*.md`. One match: use it. Multiple: present, ask. Zero: report closest candidates, exit.
2. **Pick the mode.** Default **card-decay** (audit the developed card). If the argument points at an in-progress `/develop` run (a `Research/{idea}/synthesis-handoff.md` awaiting synthesis), run **handoff-fidelity** instead.
3. **Launch the skeptic agent** (Agent tool, `subagent_type: skeptic`, fresh context) in the chosen mode. Pass the idea name and the mode.
4. **Present the verdict** the agent returns — verdict line + flags with quoted evidence and proportionate follow-ups.

## Stop Rules

| Condition | Action |
| --- | --- |
| Skeptic agent fails to launch or return | Report the failure; do not self-audit in this context — a same-session audit is the bias this skill exists to avoid. |
| Handoff-fidelity mode but no `Research/{idea}/synthesis-handoff.md` exists | Report the missing handoff; offer card-decay mode instead. |

## Scope Boundaries

This skill does NOT modify the card, re-run lenses, or trigger `/thesis-test`. Every follow-up is a recommendation for the human to act on.
