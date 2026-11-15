# Thesis-Verdict Rubric

**Loaded only when the artifact under review is a `/thesis-test` lens artifact or synthesis.** artifact-critic's default (TL;DR card / output document) checks do not apply to these artifacts — a thesis-test lens artifact is a verdict record, not a card. This rubric supplies the checks for that artifact class. The generate path never loads this file.

**Same output discipline as the base critic:** report deviations only, one per line, in the `[FIELD]: [deviation]` format. No fixes, no rewrites, no praise. If none, report `No deviations detected.` As with all evaluator loops here, **critic confirmations carry reduced weight than criticisms**, and the caller caps the revision loop at 3 iterations.

---

## What this rubric checks

### 1. Verdict-vs-evidence consistency

Each per-(break condition × thesis) verdict must be no stronger than its cited evidence supports.

- Verdict value must be one of `{HOLDS, WEAKENS, BREAKS, CONDITIONAL HOLD, UNKNOWN-INSUFFICIENT}`. Flag any value outside this set.
- Flag a `HOLDS` or `BREAKS` whose cited evidence is a single directional data point or an assertion without a source — a decisive verdict on thin evidence is over-claimed (should be `WEAKENS`, `CONDITIONAL HOLD`, or `UNKNOWN-INSUFFICIENT`).
- Flag a verdict whose cited evidence actually points the other way (evidence describes a break but the verdict says HOLDS, or vice versa).
- Flag any verdict with no cited evidence at all.

### 2. Qualifier presence on non-clean verdicts

Every `WEAKENS`, `CONDITIONAL HOLD`, and `UNKNOWN-INSUFFICIENT` must carry a free-text qualifier stating the boundary of the finding (what would move it, or what it is conditional on).

- Flag a non-clean verdict with no qualifier.
- Flag a qualifier that merely restates the verdict word without naming the boundary ("weakens because it is weak").

### 3. UNKNOWN not silent HOLDS

Where the lens had thin or no evidence for a break condition, the verdict must be `UNKNOWN-INSUFFICIENT` — not a `HOLDS` by default.

- Flag a `HOLDS` whose qualifier or evidence admits the lens could not actually test the condition (no data, out of scope, "assume it holds"). Absence of a break is not the same as survival; silent HOLDS on untested conditions is the specific failure this check guards.

### 4. Partition-format compliance

Wherever the artifact draws a strategic conclusion from evidence (in a lens roll-up's reasoning, or throughout a synthesis), it must use the mandated partition:
`Evidence: [lens found X]. Interpretation: [concludes Y because Z].`

- Flag a strategic conclusion stated without separating evidence from interpretation (roadmap-status or single-finding presented directly as a strategic conclusion — a category error where unambiguous evidence overwrites strategic interpretation).
- Flag an "Interpretation" with no "Evidence" anchor, or an "Evidence" line with no distinct interpretation (mere restatement).
- (Synthesis only) Flag if the partition is applied to some conclusions but not others.

### 5. Roll-up arithmetic sanity

Per-lens and per-thesis roll-ups must follow from their cell verdicts.

- Flag a per-thesis roll-up of `HOLDS` when one or more cells for that thesis are `BREAKS` (a break is load-bearing; the roll-up must reflect it).
- Flag a roll-up that silently drops a `BREAKS` or `UNKNOWN-INSUFFICIENT` cell.
- Flag a two-level roll-up (per-lens → per-thesis) whose top level contradicts the levels beneath it without stating why.

### 6. Synthesis-only structural checks

When the artifact is the thesis-test **synthesis** (not a lens artifact), additionally flag if any of these declared sections is absent or defaulted:

- **Recomposition or conditions** on mixed verdicts (bare stack-rank with neither → flag).
- **Premortem** tied to the surviving/recomposed position (absent, or a generic risk list not tied to that position → flag).
- **Through-line trace** to a learning/product surface (stops at a buyer/procurement surface → flag: procurement-coherent, product-incoherent).
- **Register declaration** present; persona-file gap surfaced rather than silently defaulted to generic (→ flag if defaulted).

---

## How to detect the artifact class

Treat the artifact as a thesis-test artifact (and apply this rubric instead of the card checks) when it is passed from `/thesis-test`, or when its filename or row Name matches `thesis-test-*` / `falsification-record-*`, or when its body contains a per-break-condition verdict table using the five-value verdict set. Otherwise, use the base card/output-document checks.
