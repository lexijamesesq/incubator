---
name: skeptic
description: This skill should be used when the user asks to "run the skeptic on [idea]", "is [idea] still credible", "skeptic check [idea]", or "audit [idea] against current reality". Launches the skeptic agent to audit a developed idea card's load-bearing claims (card-decay), or a /develop run's handoff fidelity when pointed at a run in progress. Reports the verdict; never modifies the card.
argument-hint: "[idea-name] [notion_ideas=...] [notion_research=...]"
context: conversation
disable-model-invocation: false
allowed-tools:
  - Read
  - Agent
  - mcp__notion__notion-fetch
  - mcp__notion__notion-query-data-sources
---

# /skeptic — Ad-Hoc Evidence Audit

The human's verb for the skeptic agent. Audits whether a developed idea's evidence is still standing — did it decay against current reality, or (when pointed at a run in progress) did the /develop handoff survive compression. Reports only; the card is never modified.

## Invocation

```text
/skeptic [idea-name]
```

## Execution

1. **Resolve the idea.** Ideas and research live in Notion; the repo's instruction file (`CLAUDE.md`, front matter) points to the Ideas database with `notion_ideas` and the Research database with `notion_research` (Read `CLAUDE.md` if the front matter is not in context; a `notion_ideas=` or `notion_research=` argument overrides the pointer for a test run). A Notion page URL as the argument is used directly. Otherwise fetch the Ideas database with `notion-fetch` and query the first view it lists with `notion-query-data-sources` in view mode (never SQL or rows mode), paging while `has_more`. Exact match on the Slug field (strip `.md` first); else case-insensitive substring match across the Slug and Name of every row. One match: use it. Multiple: present, ask. Zero: report closest candidates, exit. Notion does not return text byte for byte (a value that looks like a file name can come back wrapped as a link): compare the words, never the raw string.
2. **Pick the mode.** Default **card-decay** (audit the developed card). If the argument points at an in-progress `/develop` run (the idea row's Stage is still `seed` and its Research relation holds a `synthesis-handoff` row awaiting synthesis — fetch the idea row, then its related rows, and read each one's Research type), run **handoff-fidelity** instead.
3. **Launch the skeptic agent** (Agent tool, `subagent_type: skeptic`, fresh context) in the chosen mode. Pass the idea row's URL and the mode; in handoff-fidelity mode also pass the handoff row's URL.
4. **Present the verdict** the agent returns — verdict line + flags with quoted evidence and proportionate follow-ups.

## Stop Rules

| Condition | Action |
| --- | --- |
| Skeptic agent fails to launch or return | Report the failure; do not self-audit in this context — a same-session audit is the bias this skill exists to avoid. |
| Handoff-fidelity mode but the idea has no related `synthesis-handoff` research row | Report the missing handoff; offer card-decay mode instead. |

## Scope Boundaries

This skill does NOT modify the card, re-run lenses, or trigger `/thesis-test`. Every follow-up is a recommendation for the human to act on.
