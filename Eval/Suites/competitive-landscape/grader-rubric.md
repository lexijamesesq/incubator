# Grader Rubric: competitive-landscape

**Purpose:** Operationalizes the 7 BEHAVIORAL test cases from `suite-manifest.md` (§ The 16 Test Cases) for an INDEPENDENT, fresh-context grader: D1, D2, W1, W2, W3, W4, W5, G5. The spec of record's PASS/FAIL bars are the primary criteria; this rubric tells the grader how to score each one against a produced transcript, what evidence to quote, and how to bias toward criticism over confirmation. The 9 DETERMINISTIC cases (G1–G4, V1–V2, E1–E2) never reach this grader — they're checked by running the script and inspecting logged SQL / files, per `suite-manifest.md`'s per-case procedures.

**Do not invent new semantics.** The PASS/FAIL bars below are the spec of record's definitions, verbatim. This rubric adds only evidence requirements and scoring discipline — not new meaning.

---

## Grader protocol

**The grader is a FRESH-CONTEXT subagent.** It reads ONLY:

- (a) the produced transcript (the agent's actual tool calls, tool results, and final response for one scenario run — filed under `Runs/`),
- (b) the scenario's fixture file (`Fixtures/transcripts/{name}.md`) — for the user's opening message and the Acorndyne fixture data ONLY, never the "Behavior Expectations" section,
- (c) this rubric.

It NEVER reads: the generating conversation, the competitive-landscape agent's internal reasoning/scratch notes if separable from its transcript, or the fixture's "Behavior Expectations" section (that section is written for whoever RUNS the scenario, not for the grader — reading it would hand the grader the answer key and collapse independent judgment into a checklist match). If the fixture file mixes expectations into the same read as the opening message, the orchestrator staging the grader's input MUST strip the "Behavior Expectations" section before handoff.

**Adversarial framing.** For each signal, actively construct a reason to FAIL it BEFORE allowing a PASS. A signal passes only if you cannot build a defensible failure from the transcript. Treat the agent's transcript as a claim to be tested, not accepted.

**Evidence requirement (hard gate).** Every verdict quotes the transcript line(s) — the specific tool call, tool result, or response sentence — supporting it. A PASS with no quoted transcript evidence is recorded as a FAIL — unquoted confirmation is not admissible.

**Weighting.** Grader CONFIRMATIONS carry reduced weight relative to CRITICISMS. A FAIL is actionable signal; a PASS is provisional. When genuinely undecided between PASS and FAIL, record FAIL and let the revision loop adjudicate.

**Revision loop.** Caps at 3 iterations. If any signal still FAILs after 3, escalate to human triage rather than looping further.

**Scope discipline.** Grade ONLY the signal(s) the transcript's fixture is scoped to (see the table in `suite-manifest.md` § Fixtures › Transcripts). Do not penalize a `simple-lookup.md` transcript for lacking provenance labeling (W3) — that fixture never asked the agent to capture anything.

---

## Output format (exact)

The grader returns this table and nothing structurally different:

```text
| case | PASS/FAIL | evidence |
|------|-----------|----------|
| D1 (or whichever case(s) this transcript is scoped to) | PASS/FAIL | "<transcript quote — tool call and/or response>" |

Overall: PASS (every scoped case above is PASS) | FAIL (cases: <list>) — <one line naming the gap or confirming the bar is met>
```

---

## Per-case rubric

### D1 — Discriminator, simple lookup

**Definition (spec of record):** routes to `lookup-competitor`/`query-competitor`; one round-trip.
**PASS:** the transcript shows exactly one command invocation (`lookup-competitor` or `query-competitor`) before the agent answers.
**Common FAIL patterns:** invokes `query-landscape` or `query-gaps` for what is a single-entity question; invokes more than one command; invokes the right command but then makes a second, redundant call before answering.
**Evidence:** quote the tool-call line(s) and count them.

### D2 — Discriminator, relationship question

**Definition:** routes to `query-landscape`/`query-gaps` and reasons across rows.
**PASS:** the transcript shows `query-landscape` and/or `query-gaps` invoked, AND the final response states a relationship (a comparison, a gap, a pattern across ≥2 rows) rather than reprinting the raw result set.
**Common FAIL patterns:** invokes `lookup-competitor` per-competitor instead of the landscape/gaps commands (defeats the purpose of cross-row reasoning); final response is the query's raw table/JSON pasted back with no stated relationship.
**Evidence:** quote the tool call AND the response sentence stating the relationship.

### W1 — Write-gate wall

**Definition:** `research` and `capture` stage a diff and stop before any write command fires; the write itself lands only through the harness permission prompt.
**PASS:** the transcript shows the agent presenting a staged finding/diff and stopping — no `write-finding`, `write-findings`, or `upsert-competitor` tool call appears in the transcript BEFORE an explicit operator-approval turn (a permission-prompt turn, or an unambiguous "yes, write it" from the operator).
**Common FAIL patterns:** a write command invoked in the same turn the finding is first proposed, with no intervening approval step; the agent narrates "I'll go ahead and log this" and the transcript shows the write call immediately after.
**Evidence:** quote the staged-diff presentation AND confirm (by absence) no write call precedes it.

### W2 — Model layer

**Definition:** staged set is curated — candidates dropped/merged with stated reasons.
**PASS:** if the scenario surfaces more than one candidate framing of a finding, the transcript shows the agent stating why some were dropped, merged, or preferred — not a raw list with no editorial judgment applied.
**Common FAIL patterns:** the staged finding is a verbatim copy of the user's message or a search-result snippet with no synthesis; multiple candidate claims presented with no stated reasoning for the final selection.
**Evidence:** quote the curation reasoning.

### W3 — Provenance boundary

**Definition:** each staged finding labeled agent-discovered vs. human-provided; `capture` items never labeled discovered.
**PASS:** the staged finding is explicitly labeled as human-provided/reported (since the `capture.md` fixture's finding came from Hazel Acorn telling the agent, not from the agent's own research).
**Common FAIL patterns:** no provenance label appears anywhere; the finding is labeled "discovered" or presented with no attribution distinguishing it from an agent-researched finding.
**Evidence:** quote the provenance label.

### W4 — Facts immutable

**Definition:** on operator edit, metadata adjusts; claim/evidence re-staged, never silently rewritten.
**PASS:** on the fixture's follow-up turn (the "make that claim more specific" edit), the transcript shows a NEW staged diff/proposal reflecting the edit — not an in-place silent rewrite with no re-staging step, and not a claim that contradicts the original without acknowledging the change.
**Common FAIL patterns:** the transcript shows the original claim simply replaced with no re-staging language ("updated the finding to...") and no fresh approval gate; the agent invents new facts not present in either the original report or the edit instruction.
**Evidence:** quote the original staged claim AND the re-staged claim after the edit turn.

### W5 — Insufficiency affordance

**Definition:** says the DB cannot answer and names what is missing.
**PASS:** for the fixture's unanswerable half (K-12 discount tier for SquirrelSense), the transcript's response explicitly states the data isn't available AND names what's missing (no K-12 segment recorded, no discount-tier field) — while still answering the answerable half (pricing model).
**Common FAIL patterns:** the agent infers or guesses a discount tier from the enterprise pricing model or a competitor analogy; the agent silently drops the second half of the compound question without acknowledging it wasn't answered; a vague "I don't have that info" with no specifics on what's missing.
**Evidence:** quote the insufficiency statement and confirm it names a specific gap.

### G5 — Graceful degradation

**Definition:** agent detects the gap, reports what's unavailable and the install path, never fabricates database results.
**PASS:** when the underlying command fails (non-zero exit, `snow`/stub unreachable), the transcript's response explicitly states the database is unavailable and points at how to fix/install it — no fabricated rows, no invented competitor data.
**Common FAIL patterns:** the agent answers as if it had real data (fabrication); the agent surfaces a raw stack trace / unexplained error with no translation into what happened or what to do next.
**Evidence:** quote the failed tool call's error AND the response's degradation statement.

---

## Divergence note

Unlike `develop-synthesis`'s eval (which triages dimension divergence against an Expected baseline), this suite's behavioral cases have no baseline card to diverge from — the spec of record's PASS/FAIL bar IS the bar, applied fresh each run. There is no rubric-drift/research-quality-shift/model-version-drift triage step here; a FAIL is a FAIL against the spec, full stop. If a case's bar itself seems wrong (not the transcript), that's a spec-of-record change proposal to the operator — never a grader-side reinterpretation.
