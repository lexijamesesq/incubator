# Eval Suite: develop-synthesis

**Purpose:** Regression testing for the `develop-synthesis` agent — the strategic synthesis step of the /develop pipeline.

**Created:** 2026-03-20
**Source:** Phase 3 regression testing for the /develop pipeline
**Methodology:** Regression bar first — the bar is named before the agent changes, and an independent fresh-context grader scores each run against it.

**Fixture world:** All fixture content is fiction. It is set in one invented education market shared with the `enrichment-skills` and `thesis-test` suites: an invented company (Larkmoor Learning, with its products Coursebook and Benchmark), invented competitors, an invented regulator, and invented sources. No fixture describes a real organization, product, market, statistic, or person; every URL points at `example.com`.

---

## Fixtures

### Seeds (`Fixtures/Seeds/`)

Four seed-state idea cards. Each has the full frontmatter schema (`reference/frontmatter-schema.md`), the refined seed header fields `/develop` requires (Core insight, Source, Initial strategic connection), and an Original Capture.

| Fixture | Domain | Themes | Related Ideas | Complexity | What it stresses |
| --------- | -------- | -------- | --------------- | ------------ | ------------------ |
| absence-catch-up-pack | platform | attendance, learning-continuity | 3 siblings | High (dense portfolio area) | Two research streams that disagree; a seed connection the research overturns; three siblings to stand apart from |
| substitute-day-handover | platform | staff-cover, learning-continuity | 1 sibling | Medium (no-buyer idea) | No buyer and a cost per use; a competitive gap nobody has been asked to close; a finding with no published source |
| conference-evidence-sheet | assessments | family-communication, reporting | 2 siblings | Medium (catch-up feature) | A seed claim the research refutes (a competitor already ships it) with nothing left to differentiate on; a failed cross-domain stream |
| assessment-load-calendar | platform | student-workload | None | Low (standalone idea) | No customer mention; a failed market-sizing stream; a seed premise the handoff contradicts; a seed connection that does not hold; a capture too short for a spine snapshot |

### Handoffs (`Fixtures/Handoffs/`)

Research handoff artifacts in the synthesis-handoff format `/develop` Step 4.5 defines (`.claude/skills/develop/SKILL.md`). Each contains: Stream A (strategic context), Stream B — EdTech SME (market fit, competitive positioning, technology risk, timing), Stream B — TAM Estimate (TAM/SAM/SOM), Stream D — Educator Perspective (adoption, pain points, barriers, champion scenario), Stream C (cross-domain status line), Stream E — Divergent Reframing (a disruptive angle marked as a candidate, not evidence), Research Synthesis, Portfolio Context. Three carry the `## Spine Snapshot` section `/develop` Step 5 appends; `assessment-load-calendar` does not, because its Original Capture is under 80 words.

All four handoffs are authored, durable fixtures (not regenerated at test time). What each one puts in front of the agent:

| Handoff | Built-in condition | Signal it tests |
| --- | --- | --- |
| absence-catch-up-pack | EdTech SME reads a documented provision as what districts buy (57 of 212 RFPs, a dated directive); Educator SME says a provision the student never opens is paperwork. Research Synthesis says "Do not average them". Stream A rates the seed's family-engagement connection Weak and names a different one. One competitor finding has no link. | Honest Calibration; Mechanism-Naming (the connection has to move); Research Specificity (unlinked source cited by name) |
| substitute-day-handover | Market Fit Weak; zero RFP mentions; the budget sits in an office the company does not sell to; each use adds cost and no revenue. One finding is a single conversation with no published source. | Honest Calibration (Low is warranted); Multiplicative Framing without a revenue leg |
| conference-evidence-sheet | Stream B states the seed's "no platform produces" claim is wrong, dates the competitor's release, and says nothing would put the company ahead. Revenue evidence is two exit interviews of nine. Cross-domain failed. | Honest Calibration (a catch-up feature rated as one); Research Specificity (three named competitors and no others) |
| assessment-load-calendar | Zero NPS mentions, because the people affected are not surveyed; market sizing unavailable; Technology Risk says the product does not hold the timetable the seed assumes; the seed's design-strategy connection is rejected and one measure holds on a single study. | Honest Calibration on missing evidence; Mechanism-Naming when the seed's connection fails; Multiplicative Framing on thin support |

In every handoff the Divergent Reframing angle is absent from the Research Synthesis, so a card that cites it as evidence has taken it from Stream E.

The eval reads the handoffs directly; nothing is re-derived from a `development-research.md`.

### Expected Outputs (`Fixtures/Expected/`)

Developed cards — the regression bar.

**These four files are recorded reference runs, dated 2026-11-14.** Each is the output of one `develop-synthesis` run on its seed and handoff, unedited except that one strategy-pillar name was changed afterwards, in the cards and their handoffs alike. Run conditions:

- **How it was run:** a fresh-context agent session per idea followed `.claude/skills/develop-synthesis/SKILL.md` and adopted `.claude/agents/develop-synthesis.md`, in a staging copy holding only the seed, the handoff, the skill, the agent definition, the persona guide, and the format example. It was not invoked through the Skill tool's `context: fork`.
- **Model:** `claude-fable-5-2`. The agent definition asks for `opus`; this run did not use it.
- **Commit ref:** `44a4945` (skill and agent definition as of that commit).
- **Persona guide:** staged from `persona.sample.md`, which is a stub with no voice guidance. Voice came from the agent definition's Voice and Output Prose Translation sections.
- **Format example:** staged from `Examples/developing-card.sample.md`.
- **Grading:** each card was scored by a separate fresh-context grader that read only the card, the handoff, and `grader-rubric.md`. The graders ran on the same model at a reduced reasoning-effort setting.
- **Copy check:** each file was copied from staging after its run reported completion and compared byte for byte with the staged result, before that rename. Each Original Capture is byte-identical to its seed's.

| Fixture | Iterations | Grader result | Dimensions (CS/UX/RP/ID/SA) |
| --- | --- | --- | --- |
| absence-catch-up-pack | 2 | Iteration 1: FAIL (Multiplicative Framing). Iteration 2: PASS, all five | Medium / Medium / Medium / Medium / High |
| substitute-day-handover | 1 | PASS, all five | Medium / High / Low / Low / High |
| conference-evidence-sheet | 2 | Iteration 1: FAIL (Multiplicative Framing). Iteration 2: PASS, all five | High / Medium / Medium / Low / High |
| assessment-load-calendar | 1, on a revised handoff | PASS, all five | Low / Medium / Insufficient data / Medium / Medium |

What the iterations were:

- `absence-catch-up-pack` and `conference-evidence-sheet` each failed Multiplicative Framing on the first run. In both, the grader found the Thought Outline fanned one move out to three audiences instead of three business outcomes. The Expected file is the second run, made from the same seed and handoff with the grader's finding as an added input, which is the revision loop this suite prescribes. A second fresh grader passed all five signals on each. These two files are therefore not single clean passes.
- `assessment-load-calendar` was run twice on different inputs. The first handoff gave the idea no strategic connection that held and nothing tying it to a business outcome; the run wrote that the move "does not yet compound", and the grader failed Multiplicative Framing and Mechanism-Naming. That was a fixture too thin for the bar, so the handoff was revised (one study added, and a measure it connects to) and the idea was run again from the seed with no grader input. The Expected file is that run.

Known limits of these recordings:

- `assessment-load-calendar` has `revenue-potential: insufficient data` in its frontmatter. The agent definition tells the agent to mark a dimension "Insufficient data" when research cannot support a rating; `reference/frontmatter-schema.md` allows only null, none, low, medium, high. The card records what the agent does. The two documents disagree and this suite does not settle it. The behaviour is also not stable: the earlier run of this idea, on the first handoff and under the same unavailable market sizing, rated revenue potential Low instead.
- All four cards run 695 to 795 words above the Original Capture, counted with table syntax and link URLs. `Eval/eval-criteria.md` B20 asks for 400. That criterion is outside this suite's five signals; it is recorded here, not fixed.
- `substitute-day-handover` and `assessment-load-calendar` each carry six Open Questions; `Eval/eval-criteria.md` B14 asks for three to five.
- The graders' passes are provisional by the rubric's own weighting. The thinnest pass on every card was Multiplicative Framing.
- The graders noted small drifts that did not fail a signal: in `conference-evidence-sheet` a competitor the handoff tags "(discovered)" is cited to the competitive registry; in `substitute-day-handover` twelve comments are described as all saying what the handoff says most of them say.

---

## Quality Signals (Named Regression Bar)

Every test output is evaluated against these five signals. ALL must be present to pass. The per-card instances below are quoted from the recorded Expected cards. They illustrate the signal; a run passes on the signal, not on matching the quote.

### 1. The Experience Lens

The card frames strategy through how users encounter the capability gap, not through what the platform lacks technically.

**Signal per card:**

- **Absence pack:** "A student back from a week out queues at six desks to find out what they missed"
- **Substitute handover:** "A teacher spends her sick morning rewriting what Coursebook already holds into notes the school office prints, and the substitute who receives them has no login to see the lesson itself."
- **Conference sheet:** "Twice a year a teacher screenshots one tracker row per student, pastes it into a document and types the context underneath"
- **Load calendar:** "a head of year learns about a six-deadline Thursday after her students have lived it"

### 2. Multiplicative Framing

The Thought Outline shows one strategic move compounding across 2-3 business dimensions.

**Signal per card:**

- **Absence pack:** one page per returning student → answers the district's absence-continuity RFP (renewal revenue) → brings the student back into Coursebook on the first day back (weekly engagement) → moves past the competitor's list before its announced bundles (competitive position). The card states which links the research does not show.
- **Substitute handover:** a one-day, one-class link → the teacher gets her sick morning back (teacher goodwill) → the class does the planned lesson (lesson continuity) → the class stays in Coursebook that day (weekly return). No revenue leg, and the card says so.
- **Conference sheet:** one editable page per student → teachers prepare conferences in Benchmark (adoption) → families get the single account buyers now expect (competitive parity) → one reason for dropping Benchmark goes (renewal). The card names the last link as the weakest.
- **Load calendar:** a forward view of deadline load for the head of year → work handed in on time → students keep opening Coursebook the following week (weekly return) → a position no competing platform holds. One study carries the middle link, and the card says so.

### 3. Research Specificity

Outputs cite specific findings with concrete details — names, numbers, named capabilities.

**Examples of specificity that must survive:**

- "57 of 212 basin district RFPs issued in 2025–26"
- "A basin teacher is out a median 8 days a year, and on 61% of covered days the class does work unrelated to the current unit."
- "Corvid Classroom shipped Conference Cards in March 2026, a one-page summary per student translated into six home languages"
- "Quillfeather, a standalone homework planner where students type in their own deadlines, has 180,000 student accounts in 140 districts."

A finding the handoff gives without a link is cited by source name, unlinked. Each handoff has at least one.

### 4. Honest Calibration

Ratings show evidence of downside consideration. PASS if (a) at least one impact dimension is rated Low/None where the research warrants it, OR (b) every Medium-or-higher rating that the research complicates carries an explicit grounded counterargument or caveat traceable to the handoff. FAIL if ratings are uniformly optimistic with no grounded counterevidence, or if any rating contradicts handoff evidence without acknowledgment.

**Calibration points in the recorded cards:**

- Absence pack: no dimension rated Low/None — carried via grounded caveats on every Medium, for example Industry disruption=Medium ("Corvid already ships the simple list and has announced the next step") and User experience=Medium ("the teacher trades the paper tray for a new marking step on a day they are already behind"). The stream disagreement is kept, not averaged.
- Substitute handover: Revenue potential=Low ("every substitute login adds support cost without adding a paid seat") and Industry disruption=Low ("being first earns no competitive ground"). User experience=High is the one High the grader pressed on; it passed with the access risk carried in Open Questions.
- Conference sheet: Industry disruption=Low ("A competitor already ships this, so the sheet closes a gap and opens no lead."). Revenue potential=Medium carries its caveat ("the evidence that family reporting decides a renewal is slim").
- Load calendar: Customer sentiment=Low ("the students who feel it are never asked"). Revenue potential=Insufficient data ("a rating here would be a guess"). Strategic alignment=Medium, not High.

### 5. Mechanism-Naming Strategic Connections

Strategic connection field names the priority AND the mechanism. Not "aligns with X" but "implements X by doing Y."

**Signal per card:**

- **Absence pack:** "Advances No Lost Week, which names a student's return from absence as the first break to fix, by joining the attendance record to what each class posted"
- **Substitute handover:** "Closes the second of the three breaks No Lost Week names, a teacher's absence, by turning what the teacher has already posted into a one-day, one-class view"
- **Conference sheet:** "Implements Entered Once on the occasion the pillar itself names as the place today's record fails most visibly, by making one student's Benchmark evidence read as one account a parent can hold"
- **Load calendar:** "Supports Measure 3b (students returning to Coursebook each week) by removing the pile-up days that precede a week of lower return". The verb is "Supports"; the grader passed it on the named mechanism.

---

## Eval failure-mode framework

The eval has three independent axes that can cause produced output to diverge from expected. Triage divergence before treating it as a fail:

1. **Rubric drift (fixable in agent prompt).** Same handoff + same model + loose rubric = systematic over- or under-rating. Detected by re-running with the same handoff and seeing the same drift direction. Fix: tighten the rubric with anti-pattern guidance.
2. **Research-quality shift (legitimate).** Handoff materially deeper than the handoff that produced the expected card = ratings should evolve. A new TAM finding, a sharper competitive frame, an additional educator-sme insight may legitimately justify a higher dimension rating. The expected card is calibrated to the research available at the time; better research can move the needle.
3. **Model-version drift (expected, not necessarily a bug).** Expected cards were produced under one model version; current runs may be under a newer version. Newer models may apply rubrics more rigorously or differently. Document the model version on every eval run; expect calibration drift across major versions and treat baseline as the most recent run, not a frozen historical reference.

### Primary fail criteria (process)

The 5 quality signals above are the primary fail criteria. They hold constant across research quality and model versions. ALL must be present to pass.

### Secondary signal (calibration)

Dimension match against expected outputs is a SECONDARY signal. Divergence triggers triage along the three axes above — not auto-fail. If divergence reflects rubric drift, fix the rubric. If divergence reflects research-quality shift or model-version drift, the expected baseline may need updating rather than the agent.

### Run-record metadata

Every eval run record under `Runs/` MUST capture: date, model version, agent prompt hash or commit ref, handoff source (fixture vs. live), produced dimensions vs expected, divergence triage verdict. (`Runs/` is gitignored — run records stay local.)

## Rubric definitions

The impact-dimension definitions live in `.claude/agents/develop-synthesis.md`. They are written to stand on their own: what each dimension measures and what each level means. Lists of forbidden phrasings are not added to them. If the agent reasons soundly from the definitions and reaches a rating that differs from an Expected card, that is information for the triage above, not an automatic fail.

---

## How to Run

Each run exercises one fixture end-to-end against its durable handoff, then scores the output with an independent grader. All four handoffs are durable fixtures in `Fixtures/Handoffs/` — no handoff is re-derived at test time.

**Before the first run:** the skill loads `persona.md` and `Examples/developing-card.md` and exits if the persona guide is missing. Neither file ships in this repo; copy them from `persona.sample.md` and `Examples/developing-card.sample.md`, or use your own. Record which you used in the run report: the sample persona is a stub.

1. **Stage the seed.** Copy the seed fixture into the live pipeline: `Fixtures/Seeds/{name}.md` → `Ideas/test-{name}.md`.
2. **Stage the handoff.** Copy the durable handoff fixture into place: `Fixtures/Handoffs/{name}.md` → `Research/test-{name}/synthesis-handoff.md`. Do NOT re-derive the handoff — the handoff fixtures are the canonical research inputs.
3. **Run synthesis.** Invoke `/develop-synthesis test-{name}`. The produced card lands at `Ideas/test-{name}.md`.
4. **Grade independently.** Spawn a fresh-context grader subagent per `grader-rubric.md`. It reads ONLY the produced card, the handoff fixture (`Research/test-{name}/synthesis-handoff.md`), and `grader-rubric.md` — never this run's generating conversation and never the Expected baseline. It returns the fixed `| signal | PASS/FAIL | evidence |` table plus a one-line overall verdict. Grader confirmations carry reduced weight than criticisms; the revision loop caps at 3 iterations before human escalation.
5. **Check enrichment grounding.** Are dimension rationales and Open Questions informed by enrichment inputs? Look for: TAM reference in revenue-potential, educator-sme scenario influence in problem/UX, edtech-sme competitive window in Thought Outline, educator-sme trust barrier in Open Questions. The divergent angle should NOT appear as evidence in the card body.
6. **Compare + triage (orchestrator, not the grader).** Compare produced impact dimensions to `Fixtures/Expected/{name}.md`. The five quality signals are PRIMARY (auto-fail if missing). Dimension divergence is SECONDARY — triage across the three axes (rubric drift / research-quality shift / model-version drift) before treating it as a fail. Classify any deviation: format-level (instruction tightening) vs. reasoning-level (dimension/intent revision) vs. architecture-level (structural change).
7. **File a run report** in `Runs/{YYYY-MM-DD}-{model}-{note}.md` capturing the run-record metadata (date, model version, agent prompt/commit ref, handoff source = fixture, produced vs. expected dimensions, the grader table, divergence-triage verdict).
8. **Teardown.** Delete `Ideas/test-{name}.md` and `Research/test-{name}/`.

---

## Version History

- **2026-11-14** — Fixtures written as fiction in an invented education market: four seeds, four handoffs, four Expected cards. The Expected cards are recorded reference runs of 2026-11-14, each graded by a fresh-context grader; two took a second iteration and one was re-run on a revised handoff. Per-card signal instances and calibration points are quoted from those cards. Stale paths corrected. No signal definition changed.
- **2026-07-07** — Honest Calibration defined with two paths: a Low/None rating where warranted, or a grounded caveat on every rating the research complicates.
