# Eval Suite: thesis-test

**Purpose:** Regression testing for the `/thesis-test` skill — adversarial stress-testing of committed strategic theses against per-lens break conditions, with orchestrator-authored synthesis. This suite is the named regression bar; it was written BEFORE the skill was implemented (regression bar first).

**Created:** 2026-07-07
**Source:** The adversarial-capability and hypothesis-test-mode design work for `/thesis-test` (six design constraints).
**Methodology:** Regression bar first — the bar is named before the skill changes, and an independent fresh-context grader scores each run against it.

---

## What this suite grades

`/thesis-test` produces a chain of artifacts. The regression bar is checked across three of them:

- **Thesis brief** (`Research/{idea}/thesis-brief.md` or caller-supplied) — the committed position(s) + per-(thesis × lens) break-condition table. Signal 1 checks this.
- **Lens artifacts** (`Research/{idea}/thesis-test-{lens}-{date}.md`, one per lens) — per-break-condition verdicts with qualifiers and cited evidence, plus per-lens/per-thesis roll-ups. Signals 2 and 5 check these.
- **Synthesis** (`Research/{idea}/thesis-test-{date}.md`) — orchestrator-authored stack-rank, recomposition/conditions, premortem, through-line, register. Signals 3, 4, 5, 6 check this.

The synthesis is the load-bearing deliverable; four of six signals land on it.

---

## Fixtures

All fixture content is fiction. It is set in one invented education market shared with the `develop-synthesis` and `enrichment-skills` suites: an invented company (Larkmoor Learning, with its products Coursebook and Benchmark), invented competitors, an invented regulator (the Basin Education Authority), and invented sources. No fixture describes a real organization, product, market, statistic, or person; every URL points at `example.com`.

Two fixtures span the two modes. Per-file status is in § Staged provenance below; the traceability record is `Fixtures/traceability-2026-11-14.md`.

| Fixture | Mode | Theses | Files | Exercises |
| --- | --- | --- | --- | --- |
| `accommodations-on-classroom-checks` | card-mode | 1 | `Fixtures/Briefs/accommodations-on-classroom-checks.md` + three lens artifacts (`Fixtures/Expected/card-mode/thesis-test-{edtech-sme,tam-estimate,educator-sme}-2026-11-14.md`) + the card (`Eval/Suites/enrichment-skills/Fixtures/Ideas/accommodations-on-classroom-checks.md`). | Single-thesis card-mode; a genuine break on the edtech-sme lens (the system holding the data the thesis depends on will not release it, on two sources) while the educator lens holds; one verdict each of BREAKS, WEAKENS, CONDITIONAL HOLD, and HOLDS, with qualifiers where required; a WEAKENS that declines to become a BREAKS on one source; a reuse/re-run partition pointer; a brief that names its persona file. |
| `college-entry` | subject-mode | 3 | `Fixtures/Briefs/college-entry-subject-brief.md` + `Fixtures/Expected/subject-mode/thesis-test-2026-11-14.md`. | Multi-thesis subject-mode; **none survive cleanly → component-level recomposition** ("instructor-led dual enrolment", built from surviving parts of A, B, and C); all five verdict values including UNKNOWN-INSUFFICIENT; two-level roll-ups; dated kill criteria, one of which resolves the unknown cell; a brief that declares a missing persona file as a gap. |

A third shape — a clean survivor with conditions ("Thesis A, no breaks, four conditions for success") — is covered by the Signal 4 conditions-for-survivor path and does not have its own fixture.

### Fixture staging contract

At staging time, before any graded run:

1. Place the thesis brief + lens artifacts + (card-mode) card in `Fixtures/`.
2. Keep every fixture fictional (this is a public repo; a fixture must not carry a real organization's names, figures, or strategy).
3. Run a traceability check: every Expected quality signal must trace to a fixture line. Record it in `Fixtures/traceability-{date}.md`. A signal that cannot be traced means the fixture input is wrong — fix the input, do not blame the skill.

### Staged provenance

**Every file below is an authored reference, written 2026-11-14. None is a recorded run.** `/thesis-test` cannot be run without outside services: its three lenses do web research (which returns nothing for an invented market), it reads the learning-outcome phrasing from a private instance config, and its brief is co-drafted with a human. The Expected files show the field behavior each signal looks for; they are not a baseline to diff against. Replace them with real run output once a run on these fixtures is recorded. Each Expected file also carries `fixture-status: authored-reference` in its front matter.

| Staged fixture file | Role | Status |
| --- | --- | --- |
| `Fixtures/Briefs/accommodations-on-classroom-checks.md` | Thesis brief for the card-mode idea: one thesis, four break conditions, givens with warrants, register declaration, partition pointer | **Authored.** Its learning-outcome row carries literal phrasing, standing in for the value an installation sets under `incubator.learning_outcome_break_condition`. |
| `Fixtures/Expected/card-mode/thesis-test-edtech-sme-2026-11-14.md` | edtech-sme lens artifact, test mode | **Authored reference.** Behavior reference (Signals 2, 5 — the break). |
| `Fixtures/Expected/card-mode/thesis-test-tam-estimate-2026-11-14.md` | tam-estimate lens artifact, test mode | **Authored reference.** Behavior reference (Signal 2 — a qualified WEAKENS on one source, with no invented price). |
| `Fixtures/Expected/card-mode/thesis-test-educator-sme-2026-11-14.md` | educator-sme lens artifact, test mode, including the learning-outcome condition | **Authored reference.** Behavior reference (Signal 2). |
| `Fixtures/Briefs/college-entry-subject-brief.md` | Subject-mode brief: three rival theses, twelve break conditions | **Authored.** Written before the Expected synthesis; the break conditions do not reuse the wording of the findings. |
| `Fixtures/Expected/subject-mode/thesis-test-2026-11-14.md` | Subject-mode synthesis, with the per-break-condition verdicts and roll-ups it was built from | **Authored reference.** Field-behavior reference (Signals 2 to 6): verdict table, roll-ups, "none survive cleanly" recomposition, kill criteria, premortem, battery, signposts. |

### What a live run on these fixtures can and cannot show

The Expected files show verdicts a live run will not reproduce. Their BREAKS verdicts rest on sources that exist only inside the authored lens artifacts (for example a plan holder's customer terms). A real lens has the card, the brief, and web research that finds nothing about an invented market, so its honest verdict on most cells is UNKNOWN-INSUFFICIENT. On the subject-mode fixture, which has no card, that is the honest verdict on nearly every cell.

A live run on these fixtures can therefore be graded on Signal 1 (the brief), on Signal 2 (verdicts no stronger than their evidence, qualifiers present, UNKNOWN used where evidence is thin), and on Signal 6 (declared sections). It cannot show Signals 4 and 5 as the Expected files do, because it will not reach a grounded BREAKS. To exercise those two signals live, the evidence has to be placed where a lens can read it: either as first-pass `Research/` artifacts staged with the card, or by supplying the Expected lens artifacts as the lens outputs and running Steps 4 to 6 only. Neither is staged here; which to adopt is a decision for the suite's owner.

No lens artifacts are staged for the subject-mode fixture; its synthesis carries the verdict table. No synthesis is staged for the card-mode fixture; a run produces one from the brief.

The card-mode lens artifacts are a second lens pass over the idea — the pass run against the thesis brief. The first pass, which `/thesis-test` Step 2 partitions into reuse and re-run, is not staged: produce it by running the `enrichment-skills` suite's research-quality axis on the same card, or run with an empty `Research/` folder and accept a partition table with nothing in it.

### Detector fixture (`/develop` rubber-stamp detector)

The `/develop` rubber-stamp detector (the spine check in `.claude/skills/develop/SKILL.md` Step 9; distinct from the six thesis-test signals) needs a trip-case and a no-trip case.

- **No-trip case (staged):** a seed and the card developed from it, staged as the PAIR:
  - `Fixtures/Detector/seed-no-trip.md` — a byte-for-byte copy of `Eval/Suites/develop-synthesis/Fixtures/Seeds/absence-catch-up-pack.md`
  - `Fixtures/Detector/developed-card-no-trip.md` — a byte-for-byte copy of `Eval/Suites/develop-synthesis/Fixtures/Expected/absence-catch-up-pack.md`, which is a recorded `develop-synthesis` run of 2026-11-14 (see that suite's manifest)

  The seed's Original Capture is 127 words, so the spine check runs instead of skipping. The detector's mechanical reading of the pair: the strategic connection moved (the seed's line does not appear in the developed card); 0 of the seed capture's 3 questions survive as substrings in Open Questions (one returns reworded); the seed had no ratings. The detector trips only when the connection is unchanged and half or more of the questions survive, so this pair does not trip. The two files share their Original Capture word for word.
- **Trip case (NOT staged — do not fabricate):** to be captured from the first live `/develop` run where the detector fires, then rewritten as fiction under the staging contract. Interim reference until then: a developed card whose strategic connection restates its seed's and whose Open Questions repeat the seed's questions.

---

## Quality Signals (Named Regression Bar)

Six signals. ALL must PASS. They map to the skill's six design constraints.

### 1. Break-Condition Coverage

Before any lens runs, the thesis brief states an explicit, falsifiable break condition for EVERY (thesis × lens) pair, plus the required learning-outcome break condition. Coverage — not mere presence.

### 2. Evidence-Cited Verdicts

Every verdict in every lens artifact names the concrete evidence it rests on and carries a free-text qualifier wherever the verdict is not a clean HOLDS or BREAKS.

### 3. Partition Discipline

Every research-driven strategic conclusion in the synthesis appears in the mandated format: `Evidence: [lens found X]. Interpretation: [orchestrator concludes Y because Z].`

### 4. Recomposition-or-Conditions

When verdicts are mixed (not all theses clean-HOLD), the synthesis performs component-level recomposition across theses AND/OR states the conditions under which the surviving thesis holds. A bare stack-rank fails.

### 5. Genuine-Break Integration

A BREAKS (or decisive WEAKENS) verdict visibly changes the output — the synthesis incorporates the break rather than preserving the thesis. Fixture case: at least one hypothesis breaks and the final position reflects it.

### 6. Declared-Section Presence

The output carries the required declared sections: register declaration (audience + persona file + shape; a missing persona file surfaced as a gap, never defaulted), through-line trace, and premortem.

---

## Grader Rubric

Operationalizes the six signals for an INDEPENDENT, fresh-context grader. The signals above are the manifest's definitions; this rubric adds only PASS conditions, FAIL patterns, and evidence requirements — not new meaning.

### Grader protocol

**Fresh-context subagent.** The grader reads ONLY:

- (a) the thesis brief used for the run,
- (b) the lens artifacts produced by the run,
- (c) the synthesis produced by the run,
- (d) this rubric.

It NEVER reads: the generating conversation, the orchestrator's synthesis reasoning, or any Expected baseline. It scores the six signals ABSOLUTELY — is each present and quality, judged against the brief + lens artifacts — not by diffing against a known-good synthesis.

**Adversarial framing.** For each signal, actively construct a reason to FAIL it BEFORE allowing a PASS. A signal passes only if you cannot build a defensible failure from the artifacts. Treat the synthesis as advocacy to be tested, not accepted.

**Evidence requirement (hard gate).** Every verdict quotes the artifact line(s) supporting it. For traceability-dependent signals (2, 3, 5) also quote the upstream line (brief break condition, or lens verdict) the downstream artifact draws on. A PASS with no quoted evidence is recorded as a FAIL — unquoted confirmation is not admissible.

**Weighting (eval-isolation methodology).** Grader CONFIRMATIONS carry reduced weight relative to CRITICISMS. A FAIL is actionable signal; a PASS is provisional. When genuinely undecided between PASS and FAIL, record FAIL and let the revision loop adjudicate.

**Revision loop.** Caps at 3 iterations. If any signal still FAILs after 3, escalate to human triage rather than looping further.

**Verified-blind escalation (high-stakes runs — out-of-harness procedure, not built machinery).** For runs whose output feeds a load-bearing decision — pre-leadership-review or pre-JPD-push — the standard single fresh-context grader is insufficient isolation. The documented escalation: the operator runs a SECOND grader in a separately-spawned clean context that has never seen this run's brief-authoring or synthesis conversation, on the same rubric, and reconciles the two verdict tables by hand. Divergence between the two graders on any signal is itself the finding to act on. This is a procedure the operator invokes deliberately for high-stakes runs; the suite does not build or automate it.

### Output format (exact)

The grader returns this table and nothing structurally different:

```text
| signal | PASS/FAIL | evidence |
| --- | --- | --- |
| Break-Condition Coverage | PASS/FAIL | "<brief cells quoted>" + coverage count (N theses × 3 lenses + LO row) |
| Evidence-Cited Verdicts | PASS/FAIL | "<verdict line + cited evidence>" |
| Partition Discipline | PASS/FAIL | "<Evidence/Interpretation pair quoted>" |
| Recomposition-or-Conditions | PASS/FAIL | "<recomposition or conditions passage>" ⇐ "<verdict roll-up>" |
| Genuine-Break Integration | PASS/FAIL | "<BREAKS verdict>" ⇒ "<synthesis line that changed>" |
| Declared-Section Presence | PASS/FAIL | "<each section heading + first line>" |

Overall: PASS (all six present) | FAIL (signals: <list>) — <one line naming the gap or confirming the bar is met>
```

### Per-signal rubric

#### Rubric 1: Break-Condition Coverage

**PASS:** For N theses and 3 lenses (edtech-sme, tam-estimate, educator-sme), the brief's break-condition table carries a falsifiable "if X then this thesis weakens/breaks" entry at EVERY (thesis × lens) cell, AND the learning-outcome break-condition row is present and populated with a real product-anchored condition (not the config placeholder text).
**FAIL patterns:** a thesis covered for some lenses but not all; a "break condition" phrased as a question ("does Pennywhistle move here?" alone) or as an enrichment ask ("size the market") rather than an if-then falsification; the learning-outcome row missing, or left as the `incubator.learning_outcome_break_condition` placeholder; break conditions that read as retrofitted after the verdicts (identical wording to the finding).
**Evidence:** quote the break-condition cells; state the coverage count. Any empty cell = FAIL.

#### Rubric 2: Evidence-Cited Verdicts

**PASS:** each (break condition × thesis) verdict in the lens artifacts is one of {HOLDS, WEAKENS, BREAKS, CONDITIONAL HOLD, UNKNOWN-INSUFFICIENT}, cites at least one concrete piece of evidence (named competitor, number, policy, dated source), and every WEAKENS / CONDITIONAL HOLD / UNKNOWN-INSUFFICIENT carries a free-text qualifier stating the boundary of the finding.
**FAIL patterns:** a verdict with no cited evidence; a WEAKENS or CONDITIONAL HOLD with no qualifier; a HOLDS asserted where the qualifier itself reveals thin evidence (should be UNKNOWN-INSUFFICIENT — see §3 of `plugins/incubator/skills/artifact-critic/thesis-verdict-rubric.md`); a verdict value outside the five-value set.
**Evidence:** quote the verdict line and its cited evidence for each sampled cell.

#### Rubric 3: Partition Discipline

**PASS:** in the synthesis, each strategic conclusion that rests on lens evidence is written as an explicit `Evidence: … Interpretation: …` pair; the Evidence half states what a lens actually found, the Interpretation half states the orchestrator's judgment AND its reasoning ("because Z").
**FAIL patterns:** a strategic conclusion stated without separating evidence from interpretation (the roadmap-status-as-conclusion category error); an Interpretation with no Evidence anchor; an "Evidence" line with no distinct interpretation (mere restatement); the partition applied to some conclusions but not others.
**Evidence:** quote the conclusion(s) and confirm the mandated format.

#### Rubric 4: Recomposition-or-Conditions

**PASS:** if any thesis is WEAKENS / BREAKS / CONDITIONAL HOLD at roll-up, the synthesis either (a) recomposes surviving components across theses into a revised position (the subject-mode fixture's "instructor-led dual enrolment" — the recomposition names which components survived from which theses), or (b) states explicit conditions-under-which-the-survivor-holds ("conditions for success"), or both.
**FAIL patterns:** mixed verdicts followed by only a ranked list, no recomposition and no conditions; a survivor declared with no conditions where its verdicts were conditional; recomposition asserted but not traced to which components survived from which theses.
**N/A path:** if ALL theses clean-HOLD (grader must verify the roll-ups are genuinely clean, not inflated), the signal is vacuously satisfied → PASS; note "no mixed verdicts, N/A."
**Evidence:** quote the recomposition/conditions passage and the roll-up that triggered it.

#### Rubric 5: Genuine-Break Integration

**PASS:** locate the BREAKS (or decisive WEAKENS→BREAKS) verdict(s) in the lens roll-ups; confirm the final synthesis position differs from the pre-test committed thesis in the direction the break implies (deprioritized, reframed, dropped, or narrowed). The break must be traceable into a specific change in the position.
**FAIL patterns:** a BREAKS verdict in the lens artifacts but the synthesis preserves the original thesis unchanged (thesis-rubber-stamp — the failure mode this whole capability exists to prevent); the break acknowledged in prose but the committed position unchanged; a synthesis that only re-states surviving theses and silently drops the broken one with no reasoning.
**Evidence:** quote the BREAKS verdict and the synthesis line that changed because of it. Fixture expectation: card-mode fixture → the edtech-sme break changes where the accommodations come from, and the position keeps that they are applied; subject-mode fixture → the breaks on A and B drive the recomposition (what to leave out, and what instructor use is for). These expectations describe the authored references; see § What a live run on these fixtures can and cannot show.

#### Rubric 6: Declared-Section Presence

**PASS:** the synthesis contains all three: (a) **register declaration** — audience named, persona file named (or the absence surfaced explicitly as a gap, never silently defaulted to generic), artifact shape named; (b) **through-line trace** — the surviving position connected back through the evidence to a learning/product surface (the learning-outcome-through-line requirement); (c) **premortem** — an "it failed — why?" section tied to the surviving thesis, not a generic risk list. For card-mode, the brief also carries its register-declaration block.
**FAIL patterns:** any of the three missing; register defaulting to generic where no persona file exists (must surface the gap); through-line that stops at a procurement/buyer surface without reaching a learning/product surface (procurement-coherent, product-incoherent — the failure this section exists to catch); premortem replaced by a generic risk list not tied to the surviving thesis.
**Evidence:** quote each section heading and first line.

---

## How to Run

Each run exercises one fixture end-to-end, then scores the output with an independent grader.

1. **Stage the fixture.** Card-mode: copy the card to `Ideas/accommodations-on-classroom-checks.md` and the brief to `Research/accommodations-on-classroom-checks/thesis-brief.md`. Subject-mode: the brief stays where it is and is passed by path. The run also needs a configured instance: `.claude/instance.md` with `incubator.learning_outcome_break_condition` set (use the phrasing in the fixture brief's § 3), and `persona.md` for the card-mode register.
2. **Run thesis-test.** Invoke `/thesis-test accommodations-on-classroom-checks` (card-mode) or `/thesis-test --subject "How Larkmoor enters regional colleges" --brief Eval/Suites/thesis-test/Fixtures/Briefs/college-entry-subject-brief.md` (subject-mode). The skill produces the lens artifacts and the synthesis. The fixture market is invented, so the lenses' web research returns nothing for it; a lens that cannot find evidence should return UNKNOWN-INSUFFICIENT, and a run that does so is behaving correctly (see § What a live run on these fixtures can and cannot show).
3. **Grade independently.** Spawn a fresh-context grader subagent per § Grader Rubric. It reads ONLY the brief, the lens artifacts, the synthesis, and this rubric — never this run's generating conversation, never an Expected baseline. It returns the fixed six-row table plus a one-line overall verdict. Grader confirmations carry reduced weight than criticisms; the revision loop caps at 3 iterations before human escalation.
4. **High-stakes only:** if the run's output feeds a pre-leadership-review or pre-JPD decision, additionally run the verified-blind escalation procedure (§ Grader protocol) out-of-harness.
5. **File a run report** in `Runs/{YYYY-MM-DD}-{model}-{note}.md` capturing: date, model version, skill commit ref, fixture, lens model overrides used, the grader table, and (high-stakes) the second grader table + reconciliation.
6. **Teardown.** Remove the staged copies under `Ideas/` and `Research/accommodations-on-classroom-checks/`, and the synthesis the subject-mode run wrote.

---

## Version History

- **2026-11-14** — Fixtures written as fiction in an invented education market: two briefs, three card-mode lens artifacts, one subject-mode synthesis, the detector no-trip pair, and `Fixtures/traceability-2026-11-14.md`. All Expected files are authored references. The subject-mode fixture has three theses. Stale paths corrected. No signal changed.
- **2026-07-07** — Suite created as the regression bar for `/thesis-test`, ahead of skill implementation. Six signals named; fixtures identified; grader protocol + verified-blind escalation documented.
