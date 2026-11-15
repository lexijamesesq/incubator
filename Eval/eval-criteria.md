---
tags:
  - type/spec
  - project/incubator
created: '2026-03-11'
status: active
version: 1
---
# Incubator Eval Criteria

Defines pass/fail criteria for evaluating pipeline output quality. Used by the eval/refinement suite to score seed creation and /develop output against the template and stage mandate.

**Source of truth for constraints:** the section-scoped reference files — `reference/templates.md` (templates), `reference/stage-model.md` (stage model), `reference/architecture.md` (architecture); indexed by `incubator-reference.md`. NOT the persona guide — persona defines voice, which is evaluated separately and applies across all phases.

---

## Phase A: Seed Quality (Stage 0→1)

Evaluates router seed creation output. Source constraints: Seed Template in `reference/templates.md`.

### Structural Criteria

| ID | Criterion | Pass | Fail |
| --- | --- | --- | --- |
| A1 | Frontmatter completeness | All fields required by the frontmatter schema in `reference/frontmatter-schema.md` for the card's stage present, correct types | Missing fields, wrong types, wrong stage |
| A2 | `stage` value | `seed` | Anything else |
| A3 | Impact dimensions | All `null` | Any dimension assessed (Stage 2 work) |
| A4 | `tam-estimate` value | `null` | Any value (Stage 2+ work) |
| A5 | Filename | Kebab-case, captures core concept | Generic, misleading, or spaces |

### Content Criteria

| ID | Criterion | Template Constraint | Pass | Fail |
| --- | --- | --- | --- | --- |
| A6 | Core insight | `[One sentence — what's the idea]` | Single sentence, captures the nucleus | Multi-clause, run-on, or vague |
| A7 | Source | `[Where this came from]` | Accurate, specific | Vague or wrong |
| A8 | Initial strategic connection | `[Which current priority or theme this relates to, if apparent]` | Names one priority/theme, or "None apparent" | Over-connected (3+ priorities), vague ("aligns with strategy") |
| A9 | Original Capture | `[Verbatim original capture content]` | Complete, unmodified | Truncated, edited, reformatted, or missing |
| A10 | No development | Router constraint: "Never develop, expand, or enrich" | Seed adds structure, not analysis | Contains opportunity assessment, research, or strategic arguments |

---

## Phase B: TL;DR Quality (Stage 1→2)

Evaluates /develop output. Source constraints: TL;DR Template in `reference/templates.md` and the Stage 2 definition in `reference/stage-model.md`.

### Stage Mandate Check

The Stage 2 card answers one question: **Is this idea worth drafting?**

| ID | Criterion | Pass | Fail |
| --- | --- | --- | --- |
| B0 | Stage mandate | Card provides enough for a go/no-go decision and output format choice. Nothing more. | Card contains strategic arguments, structured analysis, or content that belongs in a Stage 3 output document |

### Header Fields

Template constraint: each field has a bracketed instruction specifying scope.

| ID | Field | Template Says | Pass | Fail |
| --- | --- | --- | --- | --- |
| B1 | Core insight | `[One sentence — confident and declarative]` | Single sentence. Declarative. States the idea, not the argument for it. | Multi-clause, hedging, argumentative, overstated |
| B2 | Problem it addresses | `[One sentence — what's broken today]` | Single sentence. Names the broken state. | Explains why it's broken, proposes the fix, or adds context |
| B3 | Who cares | `[Stakeholders/audiences affected]` | Names affected audiences by their role and need. Answers "who benefits and why." | Lists internal names, maps to OKRs, reads like an org chart |
| B4 | Strategic connection | `[How this ties to current priorities — specific, not vague]` | Names the priority and the mechanism. 1-2 sentences. | Cites 3+ strategic artifacts, reads like a compliance exercise, uses internal jargon that requires decoder ring |

### Opportunity Assessment Table

Template constraint: `[One sentence]` per rationale cell.

| ID | Criterion | Pass | Fail |
| --- | --- | --- | --- |
| B5 | Rationale cell length | Single sentence per cell | Multi-sentence, mini-paragraph |
| B6 | Rationale substance | One clear claim with supporting evidence | Vague assertion or exhaustive justification |
| B7 | Rating calibration | Rating matches rationale (not inflated) | All dimensions rated High without differentiation |

### Research Summary

Template constraint: `[Key finding with source]` × 3 examples shown.

| ID | Criterion | Pass | Fail |
| --- | --- | --- | --- |
| B8 | Bullet count | 3-5 findings | >5 (annotated bibliography) or <3 (under-researched) |
| B9 | Bullet density | Each bullet: one finding + source. Headline, not abstract. | Bullet contains market sizing, methodology details, or multi-sentence explanation |
| B10 | Source relevance | Each source directly supports the idea's viability | Tangential sources included for volume |

### Thought Outline

Template constraint: `[How this idea might develop — conceptual shape, not document structure]`

| ID | Criterion | Pass | Fail |
| --- | --- | --- | --- |
| B11 | Structure | Single paragraph, conceptual | Multiple paragraphs, bolded subheadings, structured argument |
| B12 | Scope | Describes the shape of what this could become | Develops the argument for why it should exist (Stage 3 leak) |
| B13 | Depth | Enough to see the idea's potential direction | So detailed it constrains the drafting phase |

### Open Questions

Template constraint: `[What we still don't know]`

| ID | Criterion | Pass | Fail |
| --- | --- | --- | --- |
| B14 | Question count | 3-5 | >5 (exhaustive) or <3 (surface-level) |
| B15 | Question quality | Identifies genuine unknowns that affect go/no-go | Leading questions, already-answered questions, or questions that are tasks disguised as questions |

### Voice Check

Source: `persona.md` — applied as overlay, not as density constraint.

| ID | Criterion | Pass | Fail |
| --- | --- | --- | --- |
| B16 | Corporate speak | Absent | "Leverage synergies," "holistic solution ecosystem," "facilitate stakeholder alignment" |
| B17 | Hedging | Absent | "Could potentially," "might consider," "may work if" |
| B18 | Overstating | Absent | "Unprecedented," "game-changing," "transformative" |
| B19 | Tone | Sounds like a person explaining an idea they believe in | Sounds like a consultant justifying a retainer |

### Card-Level Checks

Derived from template purpose: "scannable, shareable artifact" for "internal prioritization AND external visibility."

| ID | Criterion | Pass | Fail |
| --- | --- | --- | --- |
| B20 | Total body length | ≤400 words (excluding frontmatter and Original Capture) | >400 words |
| B21 | Scannability | Go/no-go decision reachable in <60 seconds of reading | Requires careful, multi-minute reading |
| B22 | Shareability | Card could go in a Google Doc for VP review without embarrassment or confusion | Contains internal names, assumes decoder ring, or reads as internal working notes |

---

## Scoring

Each criterion scores: **Pass**, **Marginal**, or **Fail**.

- **Pass:** Meets the constraint
- **Marginal:** Close but could be tighter (noted for iteration)
- **Fail:** Violates the constraint

**Card-level verdict:**

- **Promote:** All Pass or Marginal, no Fails → ready for human review as a real pipeline item
- **Revise:** Has Fails but the idea has value → revise with specific fixes noted
- **Drop:** Idea itself lacks strategic foundation or was misclassified

---

## Portfolio-Level Check

After scoring all cards in a run:

**The 5-minute portfolio test:** Can you read ALL developed cards in the run and rank which to draft next in under 5 minutes? If not, the cards are too dense — even if individual criteria pass.

This is the integration test. Individual criteria catch specific violations; the portfolio test catches systemic density creep.

---

## Phase C: Consolidation Quality (Step 3 Cross-Stage Awareness)

Evaluates /develop Step 3 — related idea detection, merge/keep recommendations, and merge mechanics. Source constraints: Consolidation Points in `reference/architecture.md`, stage-action table in /develop SKILL.md.

**Test dataset:** The ideas in `Ideas/` + incoming items that share a theme + theme frame edge cases. Tests span theme overlap, distinct audiences, convergent core insights, and cross-stage relationships.

### Detection Criteria

| ID | Criterion | Pass | Fail |
| --- | --- | --- | --- |
| C1 | Related items surfaced | All items sharing 2+ themes or same strategic connection are found | Misses a match that shares 2+ themes, or misses same-connection match |
| C2 | No false positives at Tier 1 | Every surfaced item genuinely shares themes or connection | Surfaces items with <2 shared themes and different connection |
| C3 | Cross-stage visibility | Related items found regardless of their stage | Only finds items at seed stage |

### Recommendation Criteria

| ID | Criterion | Pass | Fail |
| --- | --- | --- | --- |
| C4 | Merge recommendation accuracy | Recommends merge when core insights converge AND who-cares overlaps | Recommends merge for items with distinct audiences or distinct problems |
| C5 | Keep-separate accuracy | Recommends keep-separate when who-cares differs or problems are independently justifiable | Recommends keep-separate for items that are clearly the same idea |
| C6 | Stage-aware actions | Recommended actions match the stage-action table (no merge-up, no draft disruption) | Suggests merging into a drafting-stage item, or other stage-inappropriate action |
| C7 | Rationale quality | One-sentence rationale references the actual comparison (names the audience difference, or the insight convergence) | Generic rationale ("these are related") without specifics |

### Merge Mechanics Criteria

| ID | Criterion | Pass | Fail |
| --- | --- | --- | --- |
| C8 | Frontmatter merge | Themes = union, dates correct, no data loss | Missing themes from secondary, wrong dates |
| C9 | Both Original Captures preserved | Primary and secondary captures both present, labeled | Secondary capture lost or unlabeled |
| C10 | Secondary archived | Secondary row left in place, not deleted, and the human told it is merged into the primary and has to be archived by hand (Notion has no Archive location and no `archived` Stage option; see `reference/architecture.md`, Archive Conventions) | Secondary trashed, restaged to a value outside the Stage options, or left without telling the human |
| C11 | Development continues | Primary seed proceeds through remaining /develop steps normally | Merge disrupts development flow |

### Concrete Test Cases

| Test | Items | Expected Result |
| --- | --- | --- |
| Expected merge | Two seeds whose core insights converge on the same barrier, for the same audience | Recommend merge — core insights converge, who-cares overlaps |
| Expected keep-separate | Two seeds in one theme aimed at different audiences | Recommend keep separate — different audiences, different problems |
| Expected cross-stage | Seed being developed while a related idea is already at developing stage | Surface relationship, recommend developing independently (both may feed same output doc at Stage 3) |

---

## Phase B-ext: Buildable Surface Quality

Evaluates /buildable-surface output. Criteria apply only when a Buildable Surface section exists on the card. Same scoring as Phase B: Pass / Marginal / Fail.

### Detection

First principle: "Could a product team read this Thought Outline and know what to build in their first sprint?" Agent applies product-strategy judgment — no mechanical signal framework.

| ID | Criterion | Pass | Fail |
| --- | --- | --- | --- |
| BS1 | Detection accuracy | Classification matches the Thought Outline's actual product specificity. Reasoning is stated and defensible. | Classification contradicts the Thought Outline (e.g., fires on an idea that names a specific surface and commits to a single approach) |
| BS2 | Borderline honesty | Genuinely ambiguous cases flagged as borderline with reasoning | Ambiguous cases classified with false confidence in either direction |
| BS3 | Reasoning quality | "Why" explanation names what the Thought Outline does or doesn't commit to | Generic reasoning ("this is principle-shaped") without referencing the actual content |

### Candidate Quality

| ID | Criterion | Pass | Fail |
| --- | --- | --- | --- |
| BS4 | Candidate count | 3-5 candidates | <3 or >5 |
| BS5 | Distinctness | Each candidate is a genuinely different product approach | Variations of the same approach (same surface, different features) |
| BS6 | Concreteness | Each candidate names a user action ("An educator opens X and does Y") | Principles restated as features without user actions |
| BS7 | Research grounding | Each candidate connects to findings from research artifacts | Speculative candidates with no research basis |

### Card Integration

| ID | Criterion | Pass | Fail |
| --- | --- | --- | --- |
| BS8 | Voice conformance | Confident, declarative, no hedging per `persona.md` | Corporate speak, hedging, tentative language |
| BS9 | Section placement | Between Thought Outline and Open Questions | Elsewhere in the card |
| BS10 | Format compliance | Numbered list only — no sub-labels, no follow-up paragraphs | Contains sub-labels ("Feature candidates:", "Recommended surface:", "Rationale:") or follow-up paragraphs |
| BS11 | One sentence per candidate | Each candidate description fits in a single sentence | Multi-sentence candidate descriptions |
| BS12 | Card length (with Buildable Surface) | Card body ≤500 words (adjusted limit for cards with Buildable Surface section) | >500 words |

### Edge Cases

| ID | Criterion | Pass | Fail |
| --- | --- | --- | --- |
| BS13 | Borderline with existing candidates | If Thought Outline already names capabilities, generates candidates beyond what TO names | Duplicates candidates already described in the Thought Outline |
| BS14 | Pure feature no-op | Feature-shaped ideas (e.g., assessment-load-calendar) correctly no-op | Generates redundant candidates for already-specific ideas |
| BS15 | Re-run handling | Standalone: prompts before overwriting existing section. Inline /develop: overwrites (card was just written) | Silently overwrites user-modified section without prompt |

### Test Cases

| Test | Card | Expected |
| --- | --- | --- |
| Clear meta | A developed card that names several distinct problems under one heading | Fires. 3-5 candidates as numbered list |
| Clear meta | A developed card whose insight applies across several product surfaces | Fires. One candidate per surface |
| Feature | assessment-load-calendar | No-op |
| Feature | A developed card for one buildable feature | No-op |
| Borderline | substitute-day-handover | No-op or borderline flag |
| Re-run standalone | Card with existing Buildable Surface section | Prompt before overwrite |
| Re-run inline | Card just written by /develop | Overwrite without prompt |

---

## Version History

| Version | Date | Changes |
| --- | --- | --- |
| 1 | 2026-03-11 | Initial criteria. Derived from incubator-reference.md template constraints and stage mandate. |
| 2 | 2026-03-11 | Added Phase C: Consolidation Quality criteria for cross-stage awareness in /develop Step 3. |
| 3 | 2026-03-17 | Added Phase B-ext: Buildable Surface Quality criteria (BS1-BS15). First-principle detection (judgment-based, no mechanical framework), candidate quality, card integration, edge cases. Evolved through testing: v1 had 3-signal word-list detection → v2 had 2-signal test → v3 uses first-principle judgment. Dropped appetite bounding (downstream), Recommended surface/Rationale (format bloat). |
| 4 | 2026-07-07 | A1 frontmatter-completeness now points to the canonical schema in incubator-reference.md for the card's stage, instead of a hardcoded field count (was "17 schema fields"). Resolves count drift: this file said 17, an earlier scoring pass counted 16, and the live schema has grown to 22 fields (adds research-ids, jira-sidecar-url). The schema is now the single source of truth for required fields per stage. |
