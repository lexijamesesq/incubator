# Traceability: thesis-test fixtures (2026-11-14)

The staging contract in `suite-manifest.md` requires every quality signal to trace to a fixture line. This file records that check for the fixtures staged on 2026-11-14. All fixture content is fiction.

Paths are relative to `Fixtures/`.

## Signal to fixture line

| Signal | Fixture | Line it traces to |
| --- | --- | --- |
| 1. Break-Condition Coverage | `Briefs/accommodations-on-classroom-checks.md` § 2 | 1 thesis x 3 lenses + learning-outcome row = 4 cells, each an if-then. The learning-outcome row holds literal phrasing ("changes nothing a learner or teacher does inside a Larkmoor product during teaching"), not the config key. |
| 1. Break-Condition Coverage | `Briefs/college-entry-subject-brief.md` § 2 | 3 theses x 3 lenses + 3 learning-outcome rows = 12 cells, each an if-then. |
| 2. Evidence-Cited Verdicts | `Expected/card-mode/thesis-test-edtech-sme-2026-11-14.md` | BREAKS on two independent sources (the plan holder's customer terms; the data charter's restricted schedule), plus a reach figure flagged as older than 18 months. |
| 2. Evidence-Cited Verdicts | `Expected/card-mode/thesis-test-tam-estimate-2026-11-14.md` | WEAKENS, with a qualifier naming what would move it either way, on one survey; states that no price has been observed and gives no revenue figure. |
| 2. Evidence-Cited Verdicts | `Expected/card-mode/thesis-test-educator-sme-2026-11-14.md` | CONDITIONAL HOLD with its condition ("the teacher sees what will be applied before the check opens"); HOLDS on the learning-outcome row on two bases. |
| 2. Evidence-Cited Verdicts | `Expected/subject-mode/thesis-test-2026-11-14.md` § Verdicts | All five verdict values appear across 12 cells. Every cell cites evidence except C / educator-sme, which is UNKNOWN-INSUFFICIENT and says what was looked for. |
| 3. Partition Discipline | `Expected/subject-mode/thesis-test-2026-11-14.md` § Recomposition | Four `Evidence: … Interpretation: …` pairs, one per conclusion: start in the open partnerships; begin with a course new to the instructor; treat use as proof and let the district introduce; leave Benchmark out. |
| 3. Partition Discipline | the three `Expected/card-mode/` lens artifacts § Roll-up | Each lens conclusion is written as a pair. |
| 4. Recomposition-or-Conditions | `Expected/subject-mode/thesis-test-2026-11-14.md` § Recomposition | "Instructor-led dual enrolment" names what survived from which thesis: the door from C, the motion from B, what not to lead with from A's break. Four dated kill criteria follow. |
| 5. Genuine-Break Integration | `Expected/card-mode/thesis-test-edtech-sme-2026-11-14.md` § Roll-up | "Thesis A: BREAKS" on the feed's source, while the educator lens holds on the classroom effect. A synthesis from these lens artifacts must change where accommodations come from and keep that they are applied. |
| 5. Genuine-Break Integration | `Expected/subject-mode/thesis-test-2026-11-14.md` | A's edtech-sme BREAKS becomes "Benchmark is left out of the entry altogether"; B's tam-estimate BREAKS becomes "instructor use is treated as the proof and not as the sale". |
| 6. Declared-Section Presence | `Expected/subject-mode/thesis-test-2026-11-14.md` | § Register (audience, persona-file gap stated, shape); § Cross-cutting battery, through-line trace ending at an instructor teaching learners in the product; § Premortem, past tense, tied to the recomposed route. |
| 6. Declared-Section Presence | `Briefs/accommodations-on-classroom-checks.md` § 4 | The card-mode brief carries its register block and names a persona file; the subject-mode brief declares the gap. The pair covers both paths. |

## Thesis to source

| Thesis | Brief | Tested in |
| --- | --- | --- |
| A, The Plan Feed | `Briefs/accommodations-on-classroom-checks.md` | the three `Expected/card-mode/` lens artifacts |
| A placement, B instructor, C dual enrolment | `Briefs/college-entry-subject-brief.md` | `Expected/subject-mode/thesis-test-2026-11-14.md` |

## Detector pair

| Check | Result |
| --- | --- |
| `Detector/seed-no-trip.md` is identical to `../../develop-synthesis/Fixtures/Seeds/absence-catch-up-pack.md` | Yes, byte for byte. |
| `Detector/developed-card-no-trip.md` is identical to `../../develop-synthesis/Fixtures/Expected/absence-catch-up-pack.md` | Yes, byte for byte. |
| Original Capture is the same in seed and developed card | Yes, byte for byte; 127 words, so the spine check runs. |
| Strategic connection | Moved. The seed's line ("Supports the family-engagement measure by giving parents a clear list of the work their child missed.") does not appear in the developed card. |
| Seed capture questions surviving in Open Questions | 0 of 3 as substrings. One returns reworded. |
| Detector outcome | No trip: the strategic connection moved. |

## Gaps

- No card-mode synthesis is staged. Signals 3, 4, and 6 are shown at synthesis level on the subject-mode fixture only.
- No lens artifacts are staged for the subject-mode fixture; its synthesis carries the verdict table they would have produced.
- No trip-case is staged for the detector.
- The lens artifacts and the synthesis cite sources that are on no card (for example the plan holder's customer terms and the college buyers' survey). They stand for what a lens finds in its own research, and they are invented.
