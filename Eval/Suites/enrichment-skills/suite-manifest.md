# Eval Suite: enrichment-skills

**Purpose:** Verify the five enrichment skills (edtech-sme, educator-sme, divergent-thinking, tam-estimate, cross-domain) correctly handle idea mode, ad-hoc mode, fail-closed argument resolution, and augment-artifact semantics.

**Created:** 2026-04-20
**Source:** The mode-handling contract each enrichment skill states in its own SKILL.md (idea mode, ad-hoc mode, fail-closed resolution, augment artifacts).

**Execution pattern:** Manual — matches `develop-synthesis/`. Fixtures define inputs + expected behavior. A human (or future automated runner) invokes the skill on the fixture, observes, and compares against Expected/.

---

## Design principles

- **Idea mode** (naked argument): skill owns artifact write + frontmatter update. No persistence inversion. If the target artifact already exists for the same skill+idea, the skill writes a dated-suffix augment file (`{name}-{YYYY-MM-DD}.md`, counter `-2`, `-3` for same-day collisions). Original preserved. New path appended to `research: []`.
- **Ad-hoc mode** (`--adhoc "subject"`): skill operates on free-form subject string. No local artifact write, no frontmatter update. DB write-back still occurs.
- **Fail-closed idea resolution:** Zero matches → error with text pointing to `--adhoc` alternative. Never silently fall through to ad-hoc.

---

## Test cases

### Footgun (parameterized) — 5 skills × 1 test

**Input:** Invoke each skill with a typo'd idea name that matches zero filenames in `Ideas/`.

**Expected for each:**

- Exits with error (non-zero status or explicit error presentation)
- Error text includes: "Idea file not found", the typo string, closest candidates from `Ideas/`, and explicit suggestion to use `--adhoc "{typo}"` for ad-hoc analysis
- Does NOT silently proceed as ad-hoc
- Does NOT attempt database writes
- Does NOT create any files

Skills: edtech-sme, educator-sme, divergent-thinking, tam-estimate, cross-domain.

### Idea-mode fixture per skill (5)

**Input:** Invoke each skill with a naked idea-name argument referencing an existing Ideas/ file.

**Expected for each:**

- Skill loads the idea file as context
- Writes a local artifact at `Research/{idea-name}/{skill-output}.md`
  - If the file already exists, writes the dated-suffix augment (`{name}-{YYYY-MM-DD}.md`)
- Appends the written path to the idea's `research: []` frontmatter array (does not remove existing entries)
- Presentation includes idea-specific elements (impact dimension implications, research artifact path)
- DB findings written via `research-db.py write-findings` when qualifying findings exist

Skills: same five.

### Ad-hoc fixture per skill (5)

**Input:** Invoke each skill with `--adhoc "subject string"`.

**Expected for each:**

- Skill treats the subject string as the target — no Ideas/ resolution attempted
- Does NOT write any file under `Research/{idea-name}/`
- Does NOT update any idea's frontmatter
- Presentation omits idea-specific elements (no impact dimension implications, no research artifact path)
- DB findings still written when qualifying findings exist
- Competitor registry updates (where applicable) still occur

Skills: same five.

### Augment-during-refine end-to-end (1)

**Input:** An idea at `stage: refining` with an existing `Research/{idea-name}/edtech-market-analysis.md`. Human asks /refine to augment edtech-sme. /refine proposes the augment, human confirms, /refine invokes `/edtech-sme {idea-name}`.

**Expected:**

- /refine proposes the augment before invoking (does not fire autonomously)
- edtech-sme detects the existing artifact
- edtech-sme writes `Research/{idea-name}/edtech-market-analysis-{YYYY-MM-DD}.md` (new dated-suffix file)
- Original `edtech-market-analysis.md` is untouched (content unchanged)
- Idea's `research: []` array grows by one entry — the new dated-suffix path
- Original entry for `edtech-market-analysis.md` remains in the array
- DB write-back occurs for new qualifying findings

### Buildable-surface idea-only (negative test, 1)

**Input:** Invoke `/buildable-surface --adhoc "Pennywhistle Assess"`.

**Expected:**

- Skill does NOT have `--adhoc` mode
- Either the `--adhoc` flag is ignored and resolution proceeds as idea mode on "Pennywhistle Assess" (falling through to the zero-match error path), OR the skill explicitly errors on the flag
- Either way: no ad-hoc analysis produced, no DB write, no artifact

---

## Quality signals (all must pass)

1. **Fail-closed footgun prevention:** All 5 skills reject typo'd idea names with the explicit error. No silent ad-hoc fallthrough.
2. **Persistence ownership:** Idea-mode writes the artifact and updates frontmatter from inside the skill. No reliance on caller parsing markdown from the response.
3. **Ad-hoc isolation:** No local filesystem writes or frontmatter updates in ad-hoc mode. DB writes preserved.
4. **Augment coexistence:** Dated-suffix augment artifacts coexist with originals in both filesystem and `research: []` array.
5. **Description discoverability:** Each skill's description names both idea-mode and ad-hoc natural-language patterns so Claude correctly matches prompts like "edtech SME review of Pennywhistle Assess".
6. **Buildable-surface opt-out:** Skill is documented as idea-only; no `--adhoc` logic added.

---

## How to run

For each test case:

1. Set up the fixture state in `Ideas/` and `Research/` as needed (fixtures directory under this suite).
2. Invoke the skill with the specified input.
3. Observe the skill's presentation.
4. Check filesystem: `Research/{idea-name}/` contents, presence or absence of expected files.
5. Check frontmatter: `research: []` array contents.
6. Check the research database: `python3 scripts/research-db.py query-landscape ...` or by capability slug to verify findings wrote. This step needs the optional research database configured (`scripts/research-db-config.json`). Without it, record the database checks as not run; the filesystem and frontmatter checks still stand.
7. Compare against Expected/ for this test case.

Record results in `Runs/{YYYY-MM-DD}-enrichment-skills.md` (create folder as needed).

---

## Fixtures

- `Fixtures/Ideas/` — fixture idea files. It holds one card today, `accommodations-on-classroom-checks.md`, written for the research-quality axis below. The behavior tests can resolve against it: it is the existing idea for the idea-mode tests and the near-miss target for the footgun test. No minimal behavior-only card has been added.
- `Fixtures/Expected/` — expected-behavior files. It holds the three research-quality Expected files below. The behavior tests have no Expected files; their expected behavior is the text under each test case above.

The augment-during-refine test needs an idea at `stage: refining` with an existing `edtech-market-analysis.md`. No fixture stages that state; set it up by hand from the shared card.

Behavior-test fixtures are meant to be minimal — they test the skill's mode-handling logic, not the quality of its analysis. Analysis quality is covered by develop-synthesis regression bar.

**Clarification (v3):** the "intentionally minimal" posture above applies to the **behavior-test fixtures** (footgun, idea-mode, ad-hoc, augment, buildable-surface opt-out) — they exercise mode-handling logic, so a minimal idea card suffices. The **SME research-quality fixtures** added in v3 (see "Per-persona research-quality signals" below) are deliberately the opposite: they use a fully developed idea card because they test *analysis quality*, not mode handling. General develop-synthesis analysis quality still lives in the develop-synthesis suite; v3 adds a bar for the three SME lenses specifically.

---

## Per-persona research-quality signals (SME lenses)

**Scope extension (v3).** Through v2 this suite tested only mode-handling *behavior* — idea mode, ad-hoc mode, fail-closed resolution, augment coexistence. It now *also* carries a **research-quality regression bar** for three of the enrichment personas: **edtech-sme, tam-estimate, educator-sme**. These three gate Phase 2 model changes and double as thesis-test lenses, so each needs a named, checkable answer to "did this persona's research quality hold?"

This axis is **distinct from, and additive to, the behavior tests above.** The behavior tests ask "did the skill route and write correctly?"; the research-quality signals ask "is the analysis the persona produced actually good?" Both run; neither replaces the other. General develop-synthesis analysis quality remains covered by the **develop-synthesis suite** — the signals here are scoped to what these three SME lenses' own SKILL.md standards and artifact templates demand, not to synthesis-card quality. No outside frameworks are imported.

### Rubrics (the signal sets)

- `Rubrics/edtech-sme.md` — 6 signals: named-competitor differentiation, recency-stamped market intelligence, buyer/procurement dynamics named, technology-risk & regulatory grounding, competitive-window timing call, honest positioning + ARR connection.
- `Rubrics/tam-estimate.md` — 6 signals: dual-path methodology present, sourced inputs (named source + number + date), SAM/SOM narrowing + SOM cap, reconciliation between paths, conservative bias + sensitivity caveat, no-fabrication honesty.
- `Rubrics/educator-sme.md` — 6 signals: classroom-constrained adoption grounding, named pain points (felt vs. imagined), champion-vs-skeptic scenarios, pedagogical/student-outcome judgment, barrier honesty, segment sensitivity.

Each rubric entry names the signal, defines it (citing the SKILL.md standard/section it derives from), states the PASS condition and common FAIL patterns, and specifies the evidence the grader must quote.

### Fixture files

- **Shared input:** `Fixtures/Ideas/accommodations-on-classroom-checks.md` — a fully developed idea card, authored as fiction. All three personas analyze this one idea. The card is built to give each persona something to find: a complete front-matter state, every card section, three named competitors with capabilities and dates (one source older than 18 months), customer evidence split between buyer and practitioner, a retired earlier attempt at the same problem, the company's share per segment, one figure the card itself marks as unsourced, and a second segment the card marks unvalidated.
- **Expected (per persona, qualities not exact content):**
  - `Fixtures/Expected/edtech-sme-accommodations-on-classroom-checks.md`
  - `Fixtures/Expected/tam-estimate-accommodations-on-classroom-checks.md`
  - `Fixtures/Expected/educator-sme-accommodations-on-classroom-checks.md`

  **These three files are authored references, not recorded runs.** The personas need web research and, optionally, the research database, so no run was recorded when the fixtures were written. Each file applies its persona's rubric to this idea — describing the qualities the idea-mode artifact must *exhibit*, and the card line each quality draws on — and references the persona's `Rubrics/` file. They check qualities, not exact content, so a run can reach different specifics and still pass.

### How to run (research-quality axis)

For each of the three SME personas:

1. Invoke the persona in idea mode on the fixture idea (e.g., `/edtech-sme accommodations-on-classroom-checks`), with `Fixtures/Ideas/accommodations-on-classroom-checks.md` as the resolved idea. This produces the artifact under test (`edtech-market-analysis.md` / `tam-estimate.md` / `educator-evaluation.md`).
2. Hand a **fresh-context grader** three inputs only: the produced artifact, the persona's `Rubrics/{persona}.md`, and the fixture idea. Fresh context matters — the writer must not grade its own output. The Expected file is for the person running the suite; the grader does not read it.
3. The grader returns PASS/FAIL per signal and **must quote the artifact line(s)** supporting each verdict. A signal with no quotable supporting line is a FAIL.
4. The persona passes the research-quality bar only if all its signals PASS. Record results in `Runs/{YYYY-MM-DD}-enrichment-skills.md` alongside the behavior-test results.

**Provenance.** Input idea and Expected files: authored 2026-11-14 as fiction. Signal sets: authored 2026-07-07, grounded in each `plugins/incubator/skills/{persona}/SKILL.md` quality standards + artifact template.

**Fictional-market note.** The fixture idea is set in an invented education market: an invented company (Larkmoor Learning), invented competitors, an invented regulator, and invented sources, with every URL at `example.com`. It stays inside the education domain the three personas carry, with a K-12 district buyer, a classroom teacher, and a second, unvalidated college segment. A persona cannot confirm any of it by web research, and its own domain knowledge describes a different, real market. Each Expected file says how a passing artifact handles that: it works from what the card supplies, says that web research did not corroborate it, lowers its confidence, and invents nothing. `Rubrics/edtech-sme.md` Signal 1 asks for "real, identifiable" competitors; on this fixture, read that as the competitors the card names.

---

## Version history

| Version | Date | Changes |
| --- | --- | --- |
| 4 | 2026-11-14 | Fixtures written: the shared idea card `Fixtures/Ideas/accommodations-on-classroom-checks.md` and three Expected files, all authored references in an invented education market. Rubric provenance paths corrected to `plugins/incubator/`. Database check in How to run marked as needing the optional research database. No signal changed. |
| 3 | 2026-07-07 | Additive scope extension: adds a per-persona **research-quality regression bar** for the three SME lenses (edtech-sme, tam-estimate, educator-sme) via `Rubrics/` signal sets (6 named+checkable signals each) plus a shared idea-mode fixture and three authored Expected files. Does not modify the v2 behavior tests. Clarifies that the "intentionally minimal" fixtures note applies to behavior-test fixtures only. |
| 2 | 2026-04-20 | Replaces v1 entirely. v2 covers idea/ad-hoc modes, fail-closed resolution, augment coexistence, and buildable-surface opt-out. |
| 1 | 2026-04-20 | (Superseded) Original manifest. Had the caller, not the skill, write the artifact. |
