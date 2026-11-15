# Architecture: Idea Cards + Output Documents

> One section of the `incubator-reference.md` reference index — see it for the full section map.

The pipeline uses a two-track model:

**Track 1: Idea Cards (Stages 0→1→2) — Progressive Enhancement**
The idea — a row in the Ideas database in Notion, whose page body is the card and whose fields are what was front matter — progressively accumulates content. Each stage adds structure on top of what came before — nothing is discarded or overwritten.

- **Stage 0 (Capture):** Raw thought arrives from inbox — unstructured, unedited
- **Stage 1 (Seed):** Router sets the row's fields and preserves the original capture in `### Original Capture` section. /refine-seed interprets the capture and adds structured fields (core insight, source, strategic connection) before /develop runs.
- **Stage 2 (Developing):** /develop adds TL;DR sections (opportunity assessment, research summary, thought outline, open questions). Original capture persists at the bottom.

The idea card is the scannable, shareable artifact. It can be duplicated to Google Docs for peer/VP/ELT visibility into the idea portfolio. The card body freezes by default at Stage 2 — Stages 3+ create linked output documents rather than modifying the card.

**Track 2: Output Documents (Stages 3→4→5) — Linked Artifacts**
When drafting begins, /draft creates a separate output document (strategy doc or product brief): a row in the Outputs database, related to the idea row through its `Idea` relation (the idea row's `Outputs` relation stands where the `output-file` front-matter key did). The idea card body is not modified.

- **Stage 3 (Drafting):** /draft creates the Outputs row `{idea-name}-{format}`, related to the idea, and sets the idea row's `Stage` to `drafting`
- **Stage 4 (Refining):** /refine works on the output document. Idea card unchanged unless direction shifts.
- **Stage 5 (Complete):** Human approves output document. The Outputs row and the idea row get `Stage` `complete`.

**Card Update Rule:** The idea card is the source of truth for what the idea IS. If downstream work (drafting, refinement, stakeholder feedback) shifts the strategic direction, the card must be updated to reflect the new framing. Updates are deliberate, not automatic. The row's `Updated` field signals when it last changed — a card last updated at Stage 2 tells you the framing has held; a card updated during Stage 4 signals the idea evolved.

**What triggers a card update:**

- Output doc refinement shifts the strategic thesis away from the TL;DR framing
- Research during drafting invalidates or changes an impact dimension rating
- Human feedback reframes the core insight
- Consolidation with another idea changes the scope

**What does NOT trigger a card update:**

- Output doc gaining more detail (depth, not direction)
- Section-level refinements that don't change strategic framing
- Additional research supporting the existing framing

## Consolidation Points

Three natural opportunities for grouping related items:

- **Captures → Seed (0→1):** Router identifies related inbox items and proposes grouping into one seed. Human confirms.
- **Seeds → Developing (1→2):** Related-ideas matching and merge/keep-separate decisions happen in /refine-seed, before development begins. /develop Step 3 verifies the refinement is present — it checks that the `Related ideas` relation is resolved and stops if it is not. Human decides during /refine-seed.
- **Output documents (Stage 3+):** Multiple TL;DR cards can feed into a single output document. This is the natural synthesis point — a strategy doc can draw from several related idea cards. The human decides at drafting time which cards to combine.

All follow system-suggests, human-decides. No autonomous merging.

### Cross-Stage Detection

Related ideas are resolved during /refine-seed regardless of stage; /develop Step 3 verifies that resolution. What you can do depends on where the related idea is:

| Related idea stage | Available actions |
| --- | --- |
| **Seed** | Merge into one seed, or develop independently |
| **Developing** | Develop independently; both TL;DR cards may feed the same output doc at Stage 3 |
| **Drafting / Refining** | Develop independently; note the relationship for the drafter |
| **Complete** | Reference only — related work already delivered |

**Key rule:** Merge only happens between items at the same stage or when absorbing a lower-stage item. Never merge "up" or disrupt in-progress drafts.

### Merge Mechanics (Seed + Seed Only)

When the human decides to merge two seeds:

1. **Primary selection:** Human picks, or default to the seed being developed
2. **Fields:** `Themes` = union (deduplicated), `Domain`/`Source` = primary's, `Created` = earliest date, `Updated` = today
3. **Body:** Keep primary's header fields. Preserve both Original Captures:

   ```markdown
   ### Original Capture
   [Primary's original capture]

   ### Original Capture (merged from: {secondary-name})
   [Secondary's original capture]
   ```

4. **Secondary disposition:** Don't delete — provenance survives. Under files the secondary moved to `Archive/` with `stage: archived` and `archived-reason: merged-into-{primary-name}`. Notion has neither (see Archive Conventions): /refine-seed leaves the secondary row as it is and tells the human it is merged into the primary and has to be archived by hand.
5. **Continue:** Development proceeds on the primary seed with enriched context.

**Merge scope:** Seed + Seed only. Two developing cards don't merge — they stay separate and converge at the output doc layer if the human decides they belong in the same strategy doc or brief.

### Archive Conventions

Completed idea cards stay in the Ideas database with `Stage` `complete`. Completed output documents stay in the Outputs database.

Under files, an `Archive/` directory held the ideas that exited the pipeline without completing — merged items and shelved items — with `stage: archived` and an `archived-reason`. Notion has no equivalent: there is no Archive database, the `Stage` field has no `archived` option, and no row has an archived-reason field. What the skills do now:

- **Merged items:** /refine-seed merges into the primary and leaves the secondary row unchanged, at its current Stage; it tells the human the row has to be archived by hand.
- **Shelved items:** /thesis-test's shelve disposition (a human decision to park an idea) makes no write; it tells the human the row stays where it is until they archive it by hand.
- **Research:** /revert-to-seed moves an idea's own research rows to Notion's trash, where they can be restored for 30 days. No skill trashes an idea row.

A row a human has trashed is out of every skill's view: it is not in the Ideas view, so related-ideas matching does not see it.
