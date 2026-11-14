# Transcript Fixture: relationship-question

**Exercises:** D2 (discriminator — relationship question)
**Config:** `Fixtures/configs/valid.json`
**Universe:** Acorndyne (domain `acorndyne`)

## Scenario

A question that requires reasoning ACROSS competitors and capabilities —
not a single-entity fact. The correct discriminator behavior routes to
`query-landscape` and/or `query-gaps` and reasons across the returned rows
to produce a stated relationship, rather than dumping raw rows back at the
user.

## User Opening Message

> Which trackers cover soil-signal but have no yield-forecasting findings?

## Fixture Data

Acorndyne capability slugs in play: `soil-signal`, `yield-forecasting`.
Per the universe: AcornTracker covers `soil-signal` (no yield-forecasting
finding); SquirrelSense covers `soil-signal` AND `yield-forecasting` (but the
stub's `query-gaps.txt` fixture marks SquirrelSense's yield-forecasting
coverage as a GAP — no finding recorded — which is the answer this question
is fishing for). The stub's `query-gaps.txt` and `query-landscape.txt` canned
responses cover whichever command(s) the agent chooses.

## Behavior Expectations (for the run operator, not the grader)

- Agent recognizes this requires cross-competitor, cross-capability
  reasoning — not a single lookup.
- Routes to `query-landscape` and/or `query-gaps`.
- Final answer STATES the relationship (which trackers match the
  soil-signal-yes / yield-forecasting-no pattern) rather than pasting the
  raw query output back verbatim.

**D2 PASS/FAIL bar (spec of record):** PASS = routes to
`query-landscape`/`query-gaps` and reasons across rows. FAIL = returns raw
rows with no relationship stated.
