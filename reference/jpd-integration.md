# JPD Integration

> One section of the `incubator-reference.md` reference index — see it for the full section map.

## Purpose

Push developed ideas to JPD for stakeholder visibility. Query JPD during /develop for cross-domain signals.

## Configuration

All Jira/JPD connection details, field IDs and option IDs are `jira.*` keys on the Configuration page in Notion (private — they are org-specific identifiers). See `.claude/instance.sample.md` for the keys and their format.

/jpd-push and /cross-domain read those keys at runtime; a field's ID is given once, under `jira.fields`, and both skills take it from there. /cross-domain reads its optional organizational taxonomy from the page `cross_domain.org_reference` names.

**Description body:** Restructure TL;DR into JPD-compatible headings (What/Who/Why + Incubator additions). Content transferred verbatim — no generative rewriting. Exclude Original Capture only. If cross-domain research exists, include as a Cross-Domain Signals section; strip cross-domain bullets from Research Summary to avoid redundancy. See the `/jpd-push` skill for the full mapping.

## Standard JPD Idea Template

If your JPD project has an official idea template, align push output with its structure. Key fields to check:

- **Required at which stages:** Some fields (Success Measure, Cost of Delay) may only be required at later stages, not at initial Opportunity Identification.
- **Executive Summary:** Typically a pinned field (its field ID is `jira.fields.executive_summary`)
- **Description sections:** Usually What (problem statements & hypotheses), Who (audiences), Why (why worth solving), plus stage-specific fields

**Alignment with Incubator push:** Our developing-stage push uses What/Who/Why matching this convention, plus Incubator additions (Opportunity Assessment, Research Summary, Cross-Domain Signals, Thought Outline, Open Questions). We exceed what's expected at Opportunity Identification. Success Measure and Cost of Delay are not relevant at developing stage but become required at Experimentation/GTM — see the stage-aware push note below.

**Stage-aware push (future):** At later PDLC stages (Experimentation, GTM), re-push should add Success Measure and Cost of Delay per the standard template, condense Thought Outline/Open Questions as unknowns resolve, and link to a Google Doc output document rather than carrying full content inline.

## Push Criteria

Push when an idea reaches **mature developing** (TL;DR complete, impact dimensions assessed). Do not push seeds.

## JPD Sync Tracking (Idea Row Fields)

Set on the idea's row in the Ideas database after push, empty before:

| Field | Front-matter key it replaces | Holds |
| --- | --- | --- |
| `Jira key` | `jira-key` | The issue key, e.g. PROJ-1234 |
| `Jira pushed` | `jira-pushed-at` | Date of the last push |
| `Jira sidecar URL` | `jira-sidecar-url` | Google Drive URL of the Research Sidecar folder; set by /jpd-push on first push |

## Sync-Back

No automated sync-back. Any external status changes in JPD (workflow progression, roadmap priority updates, PM feedback) are learned conversationally and incorporated manually if they shift strategic direction. The incubator is not a continuous system of record — JPD push is one-directional for visibility.
