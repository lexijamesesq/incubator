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

**These four files are recorded reference runs, dated 2026-11-14.** Each is the output of one `develop-synthesis` run on its seed and handoff, and the card's words are unedited. Run conditions:

- **How it was run:** each seed and its handoff were loaded as rows in the scratch Ideas and Research databases (Loading a fixture, below), the seed under its slug with `-base` added. The skill was then invoked headless from a working copy of this repo, one idea at a time: `claude -p "/develop-synthesis {slug}-base notion_ideas=… notion_research=… notion_config=… persona_file=…"`, with the six tools in the skill's `allowed-tools` allowed and no permission prompts. Each run loaded the project-level skill and forked under the `develop-synthesis` agent (`subagent_type` in the run's stream).
- **Model:** `claude-opus-5-5` wrote every card: it is the model on every message of the forked agent. The agent definition asks for `opus`. The parent session's own model was also `claude-opus-5-5`, so the stream does not show whether the agent's `model:` was applied or the session's model inherited; either way the model is the same. The session these runs used also had an advisor tool switched on in its own settings, served by `claude-fable-5-2`, and the agent consulted it in all four runs. That is a condition of the session, not of the skill or the agent definition; a session without it may write differently.
- **Commit ref:** `994286c613a179263a871593c0d92bce04c1df18`, with uncommitted changes that became the next commit (the skill, the agent definition and the format example as that commit has them).
- **Persona guide:** a stand-in, passed as `persona_file=`: a short plain style guide written for this run (direct, concrete, no jargon), not a real persona guide. It is not kept in the repo.
- **Format example:** `Examples/developing-card.sample.md` as that commit has it, copied to the scratch page the scratch Configuration's `example_card` names.
- **Grading:** each card was scored once by a separate fresh-context grader, spawned with model `opus`, that read only the card, the handoff, and `grader-rubric.md`. No card was run again after grading: the reference is what the skill produced, and a failed signal is recorded below as the baseline's known state.
- **Copy check:** each file was built from a fetch of the finished row: the front matter is the seed's, with `stage`, `updated` and the five ratings taken from the row's fields, and the body is the row's body converted back to Markdown (`<br />` to line breaks, `<b>` to `**`, escapes removed, the table's separator row written in the form the earlier Expected files used). Each body above the Original Capture matches, word for word, the text the run sent to Notion, and each Original Capture is byte-identical to its seed's. `related-ideas` is the seed's list: the sibling ideas are not rows in the scratch database, so the row's relation was empty.

| Fixture | Runs | Grader result | Dimensions (CS/UX/RP/ID/SA) |
| --- | --- | --- | --- |
| absence-catch-up-pack | 1 | **FAIL (Multiplicative Framing).** PASS on the other four | Medium / Medium / Medium / Medium / High |
| substitute-day-handover | 1 | PASS, all five | Medium / Medium / Low / Medium / High |
| conference-evidence-sheet | 1 | PASS, all five | High / Medium / Medium / Low / High |
| assessment-load-calendar | 1 | PASS, all five | Low / Medium / Low / Medium / Medium |

Signal by signal:

| Fixture | Experience Lens | Multiplicative Framing | Research Specificity | Honest Calibration | Mechanism-Naming |
| --- | --- | --- | --- | --- | --- |
| absence-catch-up-pack | PASS | FAIL | PASS | PASS | PASS |
| substitute-day-handover | PASS | PASS | PASS | PASS | PASS |
| conference-evidence-sheet | PASS | PASS | PASS | PASS | PASS |
| assessment-load-calendar | PASS | PASS | PASS | PASS | PASS |

Known state of this baseline:

- **`absence-catch-up-pack` fails Multiplicative Framing, and the Expected file is that failing card.** The grader found that the Thought Outline fans one move out to three people ("one move serving student, teacher and district simultaneously") and never traces it to distinct business outcomes: the district's dated record is not tied to the renewals and RFPs the handoff names. A run that reproduces this card reproduces a fail. The other three Thought Outlines close on the same "one move serving…" sentence shape, which the format example also uses; they passed because the outcomes behind the names are distinct.
- **The format example changed after these cards were recorded.** When they were recorded, the shipped example card's Thought Outline ended on three people the move serves, not three business dimensions, and all four cards copied that sentence shape; it is the pattern the absence card fails on. The example now ends on adoption, retention and positioning. A card from a later run may therefore pass Multiplicative Framing where the absence card here fails it; that would be the example doing its job, not a regression.
- `assessment-load-calendar` rates Revenue potential Low, with the handoff's market sizing unavailable. The agent definition allows "Insufficient data" there, which leaves the field empty; this run did not use it, and an earlier recording of the same idea did. The behaviour is not stable.
- All four cards run 735 to 825 words above the Original Capture, counted with table syntax and link URLs. `Eval/eval-criteria.md` B20 asks for 400. That criterion is outside this suite's five signals; it is recorded here, not fixed.
- `conference-evidence-sheet` carries six Open Questions; `Eval/eval-criteria.md` B14 asks for three to five. The other three carry five.
- `substitute-day-handover` repeats both questions from its seed's capture word for word in Open Questions.
- In two runs (`absence-catch-up-pack`, `substitute-day-handover`) the agent made a third write after the body and the fields, a small edit made after its own read-back: one Thought Outline sentence split in two in the first, three words changed in a Research Summary bullet in the second. The Expected file is the row after that edit.
- The graders' passes are provisional by the rubric's own weighting. The thinnest pass on every passing card was Multiplicative Framing: on `substitute-day-handover` the grader called the competitive leg the softest, since the handoff calls that gap unvalued, and on `conference-evidence-sheet` it noted that renewal and parity overlap.
- The graders noted drifts that did not fail a signal: `substitute-day-handover` rates Industry disruption Medium with no caveat, where the handoff calls the gap "Confirmed, and unvalued". Two cards cite an unlinked finding to a source name the handoff does not give in those words: `conference-evidence-sheet` ("EdTech SME market intelligence, November 2026") and `assessment-load-calendar` ("EdTech SME market analysis, basin district RFP index 2025–26").

---

## Quality Signals (Named Regression Bar)

Every test output is evaluated against these five signals. ALL must be present to pass. The per-card instances below are quoted from the recorded Expected cards. They illustrate the signal; a run passes on the signal, not on matching the quote.

### 1. The Experience Lens

The card frames strategy through how users encounter the capability gap, not through what the platform lacks technically.

**Signal per card:**

- **Absence pack:** "a student back from a week of flu has to ask six teachers what she missed"
- **Substitute handover:** "A teacher who is ill writes her cover notes at five in the morning, the school office prints them, and on most covered days the class does work unrelated to its unit."
- **Conference sheet:** "Before each conference round a teacher opens the Benchmark tracker for every student in turn, screenshots the row, pastes it into a document and types two sentences beneath it."
- **Load calendar:** "A Year 10 student can face six deadlines on one Thursday in the week before reports, and the adults around her find out afterwards, as late work and a tired class."

### 2. Multiplicative Framing

The Thought Outline shows one strategic move compounding across 2-3 business dimensions.

**Signal per card:**

- **Absence pack (recorded as a FAIL):** one page of a returning student's missed days → the student has one place to start → her teachers are spared a rebuild by hand → the district's attendance lead has a dated record of the provision. Three people, not three business outcomes; the card does not tie the record to renewals or RFPs.
- **Substitute handover:** a one-class, one-day link → the teacher gets her sick morning back (teacher goodwill) → the class does the planned lesson and the teacher has a reason to keep her week in Coursebook (retention) → the only cover access built for one class and one day (standing against Corvid). No revenue leg, and the card says so: "It will not pay for itself."
- **Conference sheet:** an editable one-page draft per student → two weekends become an evening of edits (teacher time) → districts that weigh parent reporting have a reason to keep Benchmark (renewal) → the gap Corvid opened in March closes (competitive parity). The card calls it "a catch-up move".
- **Load calendar:** a warning to the head of year two weeks ahead → she has a reason to open Coursebook → students keep coming back the week after a crowded day (weekly return) → the only platform in the basin that shows staff a class's whole week. The card states the dependency ("Each depends on the one before") and that one study carries it.

### 3. Research Specificity

Outputs cite specific findings with concrete details — names, numbers, named capabilities.

**Examples of specificity that must survive:**

- "57 of 212 basin district RFPs issued in 2025–26 ask for absence-continuity features."
- "A basin teacher is out a median 8 days a year, and on 61% of covered days the class does work unrelated to the current unit."
- "Corvid Classroom shipped Conference Cards in March 2026: a one-page summary per student, translated into six home languages."
- "Quillfeather, a standalone homework planner, holds 180,000 student accounts in 140 districts, and its students type their deadlines in themselves."

A finding the handoff gives without a link is cited by source name, unlinked. Each handoff has at least one.

### 4. Honest Calibration

Ratings show evidence of downside consideration. PASS if (a) at least one impact dimension is rated Low/None where the research warrants it, OR (b) every Medium-or-higher rating that the research complicates carries an explicit grounded counterargument or caveat traceable to the handoff. FAIL if ratings are uniformly optimistic with no grounded counterevidence, or if any rating contradicts handoff evidence without acknowledgment.

**Calibration points in the recorded cards:**

- Absence pack: no dimension rated Low/None — carried via grounded caveats on every Medium, for example Industry disruption=Medium ("Corvid already ships the simpler list and has announced bundles, so the lead is months, not years") and User experience=Medium ("nobody knows yet whether a fourteen-year-old will open the page").
- Substitute handover: Revenue potential=Low ("each substitute is a login that adds support cost and no seat"). Customer sentiment=Medium carries its caveat ("no district or substitute has raised it"). Industry disruption=Medium carries none, which the grader noted.
- Conference sheet: Industry disruption=Low ("Corvid already prints a translated sheet for every student, so this brings Benchmark level rather than ahead."). Revenue potential=Medium carries its caveat ("a case that rests on thin evidence").
- Load calendar: Customer sentiment=Low ("the teachers and administrators Larkmoor surveys and sells to have never named it"). Revenue potential=Low ("no buyer asks for it"). Strategic alignment=Medium, not High.

### 5. Mechanism-Naming Strategic Connections

Strategic connection field names the priority AND the mechanism. Not "aligns with X" but "implements X by doing Y."

**Signal per card:**

- **Absence pack:** "Implements No Lost Week at the first break it names, a student's absence, by joining the attendance record to what each class posted"
- **Substitute handover:** "Carries No Lost Week into its second break, a teacher's absence, by handing the lesson already posted in Coursebook to whoever covers it, for one class and one day only."
- **Conference sheet:** "Implements Entered Once at the parent conference, the occasion the pillar names as its most visible failure, by putting the account Benchmark already holds onto one page per student"
- **Load calendar:** "Supports Measure 3b, students returning to Coursebook each week, by heading off the deadline pile-ups after which students open their learning platform less for a week." The verb is "Supports"; the grader passed it on the named mechanism.

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

**Loading a fixture.** The skills read and write Notion, so a fixture is loaded as rows, not staged as files. Keep a set of scratch databases with the same fields and options as the real Ideas, Research and Outputs databases, and a scratch Configuration page, and pass them to the skill as pointer overrides (`notion_ideas=`, `notion_research=`, `notion_outputs=`, `notion_config=`): a run with overrides reads and writes only what they name. A fixture file becomes a row this way: its front matter becomes the row's fields (the file name without `.md` is the Slug, the `##` title is the Name), and its body from the `##` title down becomes the row's body. `reference/skill-conventions-notion-access.md` gives the field names. A select or multi-select value a fixture uses (its `themes`, a Research type) has to be an option of the scratch field before the row is loaded: add it to the scratch database first. The steps below still name the file paths the fixtures were first staged at; read each as the row it now is. Step 1: the seed is an Ideas (scratch) row with Slug `test-{name}` and Stage `seed`. Step 2: the handoff is a Research (scratch) row, Research type `synthesis-handoff`, its `Idea` relation set to the seed row. Step 3: invoke `/develop-synthesis test-{name}` with the overrides; the card is the seed row's body afterwards. Step 4: the grader is given the card and the handoff as text fetched from those two rows. Step 8: teardown is moving the two rows to the trash by hand.

**Before the first run:** the skill loads the persona guide and the example card and exits if the persona guide is missing. Neither ships in this repo: pass `persona_file=` naming a file that holds a voice guide (or set `persona_skill` on the scratch Configuration page), and point `example_card` on that page at a Notion page holding `Examples/developing-card.sample.md` or your own example. Record which you used in the run report.

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

- **2026-11-14** — Expected cards re-recorded: each is one headless run of the skill against scratch Notion rows, forked under the `develop-synthesis` agent on `claude-opus-5-5`, graded once by a fresh-context grader and not run again. `absence-catch-up-pack` is recorded failing Multiplicative Framing. Run conditions, per-card signal results, quotes and counts rewritten from the new cards. No signal definition changed.
- **2026-11-14** — Fixtures written as fiction in an invented education market: four seeds, four handoffs, four Expected cards. Stale paths corrected. No signal definition changed.
- **2026-07-07** — Honest Calibration defined with two paths: a Low/None rating where warranted, or a grounded caveat on every rating the research complicates.
