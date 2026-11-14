# Transcript Fixture: insufficiency-case

**Exercises:** W5 (insufficiency affordance)
**Config:** `Fixtures/configs/valid.json`
**Universe:** Acorndyne (domain `acorndyne`)

## Scenario

A question the current Acorndyne fixture data provably cannot answer — no
finding, no competitor row, no capability tag covers it. The correct
behavior names what's missing rather than fabricating an answer or
stretching an adjacent finding to cover the gap.

## User Opening Message

> What's SquirrelSense's pricing model, and do they offer a K-12 discount
> tier?

## Fixture Data

Per the universe: SquirrelSense is category=emerging, market_tier=tier-3,
segments=[higher-ed], pricing_model=enterprise, capabilities=[soil-signal,
yield-forecasting]. Pricing model IS known (enterprise) — but nothing in
the fixture universe describes a K-12 discount tier, and SquirrelSense's
only recorded segment is higher-ed, not k-12. The question is a compound:
answerable in the first half, provably unanswerable in the second.

## Behavior Expectations (for the run operator, not the grader)

- Agent answers the answerable half (pricing model = enterprise) using
  `lookup-competitor`/`query-competitor`.
- For the K-12 discount question, the agent explicitly says the database
  cannot answer it and names what's missing (no K-12 segment recorded for
  SquirrelSense, no discount-tier field in the schema) — it does NOT infer
  a discount tier from the enterprise pricing model or from a competitor
  analogy, and does NOT silently drop the second half of the question.

**W5 PASS/FAIL bar (spec of record):** PASS = says the DB cannot answer and
names what is missing. FAIL = fabricates or over-reaches.
