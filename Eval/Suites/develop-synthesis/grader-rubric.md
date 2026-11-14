# Grader Rubric: develop-synthesis

**Purpose:** Operationalizes the five quality signals from `suite-manifest.md` (§ Quality Signals) for an INDEPENDENT, fresh-context grader. The five signals are the PRIMARY fail criteria; this rubric tells the grader how to score each one, what evidence to quote, and how to bias toward criticism over confirmation.

**Do not invent new semantics.** The signal definitions below are the manifest's definitions. This rubric adds only PASS conditions, FAIL patterns, and evidence requirements — the operational scaffolding — not new meaning.

---

## Grader protocol

**The grader is a FRESH-CONTEXT subagent.** It reads ONLY:

- (a) the produced card (`Ideas/test-{name}.md`),
- (b) the handoff fixture (`Research/test-{name}/synthesis-handoff.md`),
- (c) this rubric.

It NEVER reads: the generating conversation, the `develop-synthesis` agent's reasoning, or the Expected baseline card (`Fixtures/Expected/{name}.md`). Reading the baseline would collapse independence into diffing. The grader scores the five signals ABSOLUTELY — is each signal present and quality, judged against the handoff — not by comparison to a known-good card. Baseline comparison and divergence triage are the orchestrator's job (see § Divergence triage), performed on the grader's output, not inside the grader.

**Adversarial framing.** For each signal, actively construct a reason to FAIL it BEFORE you allow a PASS. A signal passes only if you cannot build a defensible failure from the card + handoff. Treat the card as advocacy to be tested, not accepted.

**Evidence requirement (hard gate).** Every verdict quotes the card line(s) supporting it. For traceability-dependent signals (Research Specificity, Honest Calibration, Mechanism-Naming), also quote the handoff line the card draws on. A PASS with no quoted card evidence is recorded as a FAIL — unquoted confirmation is not admissible.

**Weighting (eval-isolation methodology).** Grader CONFIRMATIONS carry reduced weight relative to CRITICISMS. A FAIL is actionable signal; a PASS is provisional. When genuinely undecided between PASS and FAIL, record FAIL and let the revision loop adjudicate.

**Revision loop.** Caps at 3 iterations. If any signal still FAILs after 3, escalate to human triage rather than looping further.

---

## Output format (exact)

The grader returns this table and nothing structurally different:

```text
| signal | PASS/FAIL | evidence |
|--------|----------|----------|
| Experience Lens | PASS/FAIL | "<card quote>" (+ handoff quote if relevant) |
| Multiplicative Framing | PASS/FAIL | "<card quote>" |
| Research Specificity | PASS/FAIL | "<card claim>" ⇐ "<handoff line>" (per claim) |
| Honest Calibration | PASS/FAIL | "<ratings + counterargument>" ⇐ "<handoff basis>" |
| Mechanism-Naming Strategic Connection | PASS/FAIL | "<card quote naming priority + mechanism>" |

Overall: PASS (all five present) | FAIL (signals: <list>) — <one line naming the gap or confirming the bar is met>
```

---

## Per-signal rubric

### 1. The Experience Lens

**Definition (manifest):** The card frames strategy through how users encounter the capability gap, not through what the platform lacks technically.
**PASS:** The card (typically Core insight, Problem, or Thought Outline) puts a real user in a scene hitting the gap — a person doing a task and running into the wall — rather than stating a technical deficit.
**Common FAIL patterns:** Opens with platform/technical framing ("the platform has no rubric-scoring API"); abstract capability language with no human in the scene; a feature list with no user encountering it.
**Evidence:** Quote the card sentence that stages the user encounter (or the technical-framing sentence if failing).

### 2. Multiplicative Framing

**Definition (manifest):** The Thought Outline shows one strategic move compounding across 2-3 business dimensions.
**PASS:** The Thought Outline names a SINGLE move and traces it compounding across 2-3 GENUINELY DISTINCT business dimensions (e.g., adoption + retention + infrastructure). The labels the manifest uses per card are illustrative — accept any 3 distinct business outcomes so long as they trace to one move.
**Common FAIL patterns:** Single-dimension benefit; a list of unrelated benefits not tied to one move; two "dimensions" that are rephrasings of each other; compounding asserted but not traceable to a business outcome.
**Evidence:** Quote the Thought Outline sentence(s) showing one move → multiple distinct dimensions.

### 3. Research Specificity

**Definition (manifest):** Outputs cite specific findings with concrete details — names, numbers, named capabilities.
**PASS:** The Research Summary and body cite specific, concrete facts — named competitors, numbers/percentages, named capabilities or policies — and EACH traces to the handoff.
**Common FAIL patterns:** Vague findings ("the market is growing," "competitors exist"); a named competitor, number, or policy that does NOT appear in the handoff (fabrication — auto-FAIL for that claim, and FAIL the signal); round unsourced figures presented as findings.
**Evidence:** For each specific claim, quote it AND the handoff line it traces to. A specificity claim with no handoff support is a FAIL. (Reference case: a competitor named in the card but absent from the handoff fails, even if the other named competitors trace.)

### 4. Honest Calibration

**Definition (manifest):** Ratings show evidence of downside consideration.
**PASS:** (a) At least one impact dimension is rated Low/None where the research warrants it, OR (b) every Medium-or-higher rating that the research complicates carries an explicit grounded counterargument or caveat traceable to the handoff.
**FAIL:** Ratings are uniformly optimistic with no grounded counterevidence, OR any rating contradicts handoff evidence without acknowledgment.
**Common FAIL patterns:** All dimensions High/Medium with no differentiation and no grounded caveat; a weak dimension inflated above what the handoff supports; a dimension the handoff clearly rates Low presented as Medium/High with no acknowledgment; no counterargument anywhere (pure advocacy).
**Evidence:** Quote the dimension ratings + the counterargument/caveat line, and the handoff basis for the rating it complicates (path b) or for the Low/None-rated dimension (path a).

### 5. Mechanism-Naming Strategic Connection

**Definition (manifest):** The strategic connection names the priority AND the mechanism — not "aligns with X" but "implements X by doing Y."
**PASS:** The Strategic connection field (and/or Thought Outline) names a SPECIFIC priority/initiative AND the mechanism by which the idea advances it ("implements X by doing Y").
**Common FAIL patterns:** "Aligns with / supports / relates to X" with no mechanism; a mechanism named but no priority; vague strategic hand-waving; a decoder-ring pile of initiative names with no causal verb.
**Evidence:** Quote the strategic-connection sentence and confirm it contains BOTH a named priority AND a named mechanism.

---

## Divergence triage (orchestrator, not the grader)

The grader scores the five PRIMARY signals absolutely. Impact-dimension divergence from the Expected baseline is a SECONDARY signal and is handled by the orchestrator AFTER the grader returns — the grader never sees the baseline. Before recording a dimension divergence as a fail, triage it across the three axes from `suite-manifest.md`:

1. **Rubric drift** (fixable in agent prompt) — same handoff + same model + loose rubric producing systematic over/under-rating. Fix: tighten the rubric.
2. **Research-quality shift** (legitimate) — handoff materially deeper than the one that produced the Expected card; ratings may legitimately evolve. Fix: consider re-baselining the Expected card, not the agent.
3. **Model-version drift** (expected) — Expected produced under an older model; newer models may apply rubrics differently. Document the model version; treat the most recent run as the baseline, not a frozen historical reference.

A PRIMARY-signal FAIL from the grader is actionable directly. A SECONDARY dimension divergence goes through triage before any fix. Record the model version and handoff source (fixture vs. live) on every run per the manifest's run-record metadata requirement.
