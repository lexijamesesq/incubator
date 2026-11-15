# Shared Research

> One section of the `incubator-reference.md` reference index — see it for the full section map.

Cross-idea research findings that compound across pipeline runs. Stored in the Snowflake `research_findings` table, queried via `scripts/research-db.py`.

## Topics

Findings are tagged with a `topic` value that groups them by concern:

| Topic | Contents | Primary Skills |
| --- | --- | --- |
| `customer-evidence` | Pain signals, adoption behavior, research validation | /develop (Stream A), /educator-sme |
| `competitive-landscape` | Named competitors, specific capabilities, competitive gaps | /develop (Stream B), /edtech-sme |
| `market-sizing` | TAM figures, growth rates, segment data | /tam-estimate |

Skills query the database at research start (`query-landscape`) to establish a baseline, then write qualifying findings back (`write-findings`) at the end of the run.

## Capture Heuristic

A finding qualifies for shared research when ALL four criteria are met:

1. **Sourced** — Named, verifiable source with specific data and a URL (the most specific available page — press release, blog post, report page — not a homepage)
2. **Durable** — Useful beyond 3 months (not ephemeral news or announcements)
3. **Decision-relevant** — Tied to a named impact dimension with a specific directional effect
4. **Shared** — Relevant beyond the current idea, or likely relevant to future ideas entering the pipeline

**Don't capture:** General trend statements, single-idea findings (those go in the idea's rows in the Research database), ephemeral news, unsourced opinions, interpretations or trend extrapolations.

## Governance

- **Autonomous writes:** Skills evaluate findings against the capture heuristic and write qualifying entries directly to Snowflake via `research-db.py write-findings`. The heuristic (Sourced + Durable + Decision-relevant + Shared) is the quality gate — no human confirmation step.
- **Non-retroactivity:** Shared research informs future /develop runs only. New findings do not trigger updates to ideas that have already passed Stage 2. Past cards are revisited only if the human explicitly requests it.
- **TTL by category:** Each entry has a category with a defined TTL (see table below). Reading skills treat expired entries as directional only — reverify before citing.
- **Supersession:** Stale findings are not deleted — the newer finding points to the older via `superseded_by`. Query results filter `superseded_by IS NULL` to retrieve the current view.

## TTL Reference

| Category | TTL |
| --- | --- |
| `pain-signal` | 12 months |
| `adoption-signal` | 12 months |
| `research-validation` | 24 months |
| `capability-specific` | 12 months |
| `capability-presence` | 18 months |
| `competitive-gap` | 12 months |
| `tam-broad` | 36 months |
| `tam-segment` | 24 months |
| `growth-rate` | 24 months |

## Integration with Idea Cards

Shared findings in the Snowflake database are NOT linked in the idea row's `Research` relation (that stays for the idea's own artifact rows). When a shared finding materially influences an idea's Research Summary or impact dimension rating, cite it with the original external source link from the finding's `source_url` — the same format as any other Research Summary citation: `([Source Title](url))`. No internal file paths, no provenance tags. Provenance metadata (origin idea, date created, confidence) stays on the finding row in the database.

## Verification at /draft and /refine

/draft and /refine must verify shared competitive claims before asserting them in stakeholder-facing documents. Shared findings are a dated baseline — treat as starting point for verification, not settled fact, when the output goes to VP/ELT audiences.
