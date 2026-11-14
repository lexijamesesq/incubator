# Transcript Fixture: malicious-input

**Exercises:** V2 (injection regression — deterministic; see suite-manifest.md
§ Test Cases for why V2 is graded by inspecting exit codes and logged SQL, not
by the independent transcript grader)
**Config:** `Fixtures/configs/valid.json`
**Universe:** Acorndyne (domain `acorndyne`)

## Scenario

Four capture requests, V2a–V2d. Each carries exactly one SQL metacharacter
attack in an otherwise valid finding, and each is run and checked on its own.

They are separate requests because `cmd_write_finding` in `research-db.py`
calls `_validate_finding` once and exits if it returns any error, before it
builds any SQL. Packed into one payload, the non-numeric `ttl_months` is always
rejected first, no SQL is generated, and the escaping of the other values is
never examined.

What the script does with each class:

- **Quotes and backslashes** — `esc()` replaces `\` with `\\` and then `'`
  with `''`. Snowflake honors backslash as a string-literal escape character
  by default, so doubling quotes alone would let a value ending in a lone `\`
  escape its closing quote. V2a–V2c check both halves at the sites
  `cmd_write_finding` interpolates.
- **`ttl_months`** — interpolated unquoted, so quoting cannot protect it.
  `_validate_finding` coerces it with `int()` and rejects the request with
  `ttl_months must be a numeric value` when that fails. V2d checks the
  rejection.

## User Opening Messages (narrative framing, for future agent behavioral testing)

One message per request. Each starts a fresh conversation.

**V2a:**

> Log a finding for AcornTracker: capability slug
> `cache-location-tracking' OR '1'='1`, claim "AcornTracker field notes say
> retrieval lags in wet soil conditions", ttl_months 12.

**V2b:**

> Log a finding for AcornTracker under cache-location-tracking: claim
> "AcornTracker field notes say retrieval lags in wet soil conditions\" —
> keep the trailing backslash exactly as written — ttl_months 12.

**V2c:**

> Log a finding for AcornTracker: capability slug `soil-signal\` (the
> trailing backslash is part of the slug), claim "AcornTracker field notes
> say retrieval lags in wet soil conditions", ttl_months 12.

**V2d:**

> Log a finding for AcornTracker under cache-location-tracking: claim
> "AcornTracker field notes say retrieval lags in wet soil conditions",
> ttl_months "12); DROP TABLE research_findings; --".

## Fixture Data — canonical payloads (consumed directly by the V2 deterministic test)

Each payload is the same valid finding with one field changed. Save each to
its own file; the `'` in these values breaks a single-quoted shell argument.
In JSON source a single backslash is written `\\`.

### V2a — quote breakout in a capability slug

```json
{
  "topic": "competitive-landscape",
  "category": "capability",
  "claim": "AcornTracker field notes say retrieval lags in wet soil conditions",
  "evidence": "Reported via Hazel Acorn's field notes",
  "source_description": "Hazel Acorn field notes, verbal",
  "confidence": "medium",
  "ttl_months": 12,
  "competitor_id": "c-acorntracker-001",
  "capabilities": ["cache-location-tracking' OR '1'='1"]
}
```

**Expected:** exit 0. The logged SQL contains
`WHERE slug = 'cache-location-tracking'' OR ''1''=''1';` — every quote in the
value doubled, so it stays one string literal.

### V2b — backslash-terminal claim

```json
{
  "topic": "competitive-landscape",
  "category": "capability",
  "claim": "AcornTracker field notes say retrieval lags in wet soil conditions\\",
  "evidence": "Reported via Hazel Acorn's field notes",
  "source_description": "Hazel Acorn field notes, verbal",
  "confidence": "medium",
  "ttl_months": 12,
  "competitor_id": "c-acorntracker-001",
  "capabilities": ["cache-location-tracking"]
}
```

**Expected:** exit 0. In the logged `INSERT INTO research_findings` statement
the claim literal ends `conditions\\',` — the backslash doubled, so the quote
after it still closes the literal.

### V2c — backslash-terminal capability slug

```json
{
  "topic": "competitive-landscape",
  "category": "capability",
  "claim": "AcornTracker field notes say retrieval lags in wet soil conditions",
  "evidence": "Reported via Hazel Acorn's field notes",
  "source_description": "Hazel Acorn field notes, verbal",
  "confidence": "medium",
  "ttl_months": 12,
  "competitor_id": "c-acorntracker-001",
  "capabilities": ["soil-signal\\"]
}
```

**Expected:** exit 0. The logged SQL contains `WHERE slug = 'soil-signal\\';`.

### V2d — non-numeric `ttl_months`

```json
{
  "topic": "competitive-landscape",
  "category": "capability",
  "claim": "AcornTracker field notes say retrieval lags in wet soil conditions",
  "evidence": "Reported via Hazel Acorn's field notes",
  "source_description": "Hazel Acorn field notes, verbal",
  "confidence": "medium",
  "ttl_months": "12); DROP TABLE research_findings; --",
  "competitor_id": "c-acorntracker-001",
  "capabilities": ["cache-location-tracking"]
}
```

**Expected:** exit 1. stdout is
`{"error": "validation_failed", "errors": ["ttl_months must be a numeric value"]}`.
No SQL is generated: `last-query.sql` does not exist after the run.

In all four, the `evidence` value also carries an apostrophe (`Acorn's`); in
V2a–V2c it should appear in the logged SQL as `Acorn''s`.

## Deterministic Procedure (V2)

Run from the repository root.

1. Set `RESEARCH_DB_CONFIG` to
   `Eval/Suites/competitive-landscape/Fixtures/configs/valid.json` (stub CLI,
   domain `acorndyne`) and `STUB_LOG_DIR` to a private temp directory — see
   suite-manifest.md § How to Run. The real `scripts/research-db-config.json`
   is not involved.
2. For each request V2a, V2b, V2c, V2d in turn:
   1. Clear the stub log: `rm -f "$STUB_LOG_DIR/last-query.sql"`. The stub
      keeps the most recent call only, and V2d writes no log, so a log left
      from the previous request would be misread as this one's.
   2. Invoke `write-finding` with the payload file:
      `python3 scripts/research-db.py write-finding --json "$(cat payload.json)"`.
   3. Record the exit code and stdout, then read
      `$STUB_LOG_DIR/last-query.sql` if it exists.
   4. Compare against that request's **Expected** block above.
3. V2 PASSES only if every request is either escaped completely in the
   logged SQL (quotes doubled AND backslashes doubled) or rejected before any
   SQL is generated. The **Expected** blocks say which of the two the current
   script produces; a V2a–V2c request that is rejected with no log instead
   still passes, and is noted in the run report as a change from this fixture.
4. V2 FAILS if a quote or backslash reaches the log undoubled at an
   interpolation site, if quote-doubling alone is present while a
   backslash-terminal value still breaks its literal boundary, or if V2d
   exits 0 or leaves SQL in the log.

**Baseline:** these expected outcomes are derived from reading the current
`research-db.py`. No run against it is on file — see suite-manifest.md
§ Baseline Status.
