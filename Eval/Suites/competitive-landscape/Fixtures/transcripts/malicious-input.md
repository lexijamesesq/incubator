# Transcript Fixture: malicious-input

**Exercises:** V2 (injection regression — deterministic; see suite-manifest.md
§ Test Cases for why V2 is graded by inspecting logged SQL, not by the
independent transcript grader)
**Config:** `Fixtures/configs/valid.json`
**Universe:** Acorndyne (domain `acorndyne`)

## Scenario

A capture request whose values carry SQL metacharacters — including a
backslash-terminal payload that defeats quote-doubling-only escaping (see
`research-db.py:72–76` `esc()` — doubles `'` only; Snowflake honors
backslash as a string-literal escape character by default, so a value
ending in a lone `\` right before the closing quote can escape the quote
and bleed attacker content into raw SQL). This fixture supplies the exact
payload values the deterministic V2 test runs against `write-finding`.

## User Opening Message (narrative framing, for future agent behavioral testing)

> Log a finding for AcornTracker: capability slug
> `cache-location-tracking' OR '1'='1`, claim "field notes say retrieval
> lags in wet soil\", ttl_months "12); DROP TABLE research_findings; --".

## Fixture Data — canonical malicious payload (consumed directly by the V2 deterministic test)

```json
{
  "topic": "competitive-landscape",
  "category": "capability",
  "agent_type": null,
  "claim": "AcornTracker field notes say retrieval lags in wet soil conditions\\",
  "evidence": "Reported via Hazel Acorn's field notes",
  "source_description": "Hazel Acorn field notes, verbal",
  "confidence": "medium",
  "ttl_months": "12); DROP TABLE research_findings; --",
  "competitor_id": "c-acorntracker-001",
  "capabilities": ["cache-location-tracking' OR '1'='1", "soil-signal\\"]
}
```

Payload classes present (each MUST be defeated — quote-doubling alone is
insufficient per the spec note):

- **Quote-based injection:** `cache-location-tracking' OR '1'='1` (capability
  slug), classic `'` breakout.
- **Backslash-terminal payload:** `claim` field and the `soil-signal\`
  capability slug both end in a lone backslash immediately before where the
  closing `'` would land — this is the payload class `esc()`'s
  quote-doubling-only approach does NOT neutralize, because Snowflake
  honors `\` as the default string-literal escape character.
- **Non-numeric `ttl_months`:** `"12); DROP TABLE research_findings; --"` —
  `ttl_months` is interpolated unquoted/unvalidated
  (`{args["ttl_months"]}` in `cmd_write_finding`), so a non-numeric string
  here is a raw-injection vector, not a quoting problem.

## Deterministic Procedure (V2)

1. Point `research-db-config.json` at `Fixtures/configs/valid.json` (stub
   CLI, domain `acorndyne`).
2. Invoke `python3 scripts/research-db.py write-finding --json '<payload
   above>'`.
3. Read `$STUB_LOG_DIR/last-query.sql` (default
   `/tmp/research-db-stub-log/last-query.sql`).
4. PASS requires ONE of:
   - The command is rejected before any SQL reaches the stub (input
     validated and refused — `ttl_months` numeric check would catch the
     non-numeric case), OR
   - The logged SQL shows dialect-complete escaping: quotes doubled AND
     backslashes escaped/neutralized at every interpolation site
     (capability slug, claim, ttl_months).
5. FAIL if ANY metacharacter class passes through unescaped at ANY
   interpolation site, OR if quote-doubling alone is treated as sufficient
   while the backslash-terminal payload still breaks the literal boundary.

**Known pre-implementation state (informational, not a G3-style required
delta):** the current unmodified `research-db.py` has no `ttl_months`
numeric validation and `esc()` performs quote-doubling only — this fixture
is expected to demonstrate the gap V2 exists to catch, once the guard work
(scoped to a later build item than this suite) lands.
