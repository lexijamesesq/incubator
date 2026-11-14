# Transcript Fixture: simple-lookup

**Exercises:** D1 (discriminator — simple lookup)
**Config:** `Fixtures/configs/valid.json`
**Universe:** Acorndyne (domain `acorndyne`)

## Scenario

A single, narrow factual question about one named competitor. The correct
discriminator behavior is to route directly to `lookup-competitor` and/or
`query-competitor` — a single round-trip — not to fan out into a multi-command
analysis pass (that's D2's job).

## User Opening Message

> What tier is AcornTracker?

## Fixture Data

None beyond the standard Acorndyne universe (AcornTracker: category=core,
market_tier=tier-1, segments=[k-12], pricing_model=per-student,
capabilities=[cache-location-tracking, soil-signal]). The stub CLI's
`lookup-competitor-acorntracker.json` and `query-competitor.txt` canned
responses cover whichever command the agent chooses.

## Behavior Expectations (for the run operator, not the grader)

- Agent recognizes this as a narrow, single-entity lookup — not a landscape
  or gap question.
- Routes to `lookup-competitor` and/or `query-competitor`. One round-trip:
  no `query-landscape`, no `query-gaps`, no multi-command fan-out.
- Answer states the tier (tier-1) directly, citing the competitor by name.

**D1 PASS/FAIL bar (spec of record):** PASS = routes to
`lookup-competitor`/`query-competitor`, one round-trip. FAIL = fans out
multi-command analysis for what is a single-fact question.
