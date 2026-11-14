# Rubric: educator-sme research-quality signals

**Provenance:** Signal set authored 2026-07-07, grounded in `plugins/incubator/skills/educator-sme/SKILL.md` (Step 3 five dimensions, artifact template) and `plugins/incubator/agents/educator-sme.md` (Evaluation Framework, Quality Standards, Domain Calibration).

**What this rubric is for:** The named, checkable regression bar for "did educator-sme's *research quality* hold?" It is distinct from the suite's mode-handling behavior tests (idea/ad-hoc/fail-closed). It gates Phase 2 model changes and serves as a thesis-test lens. Every signal derives from what the persona's own standards already demand — no outside frameworks are imported.

**Scope note:** These signals check the produced artifact's evaluation quality. They do NOT check general develop-synthesis card quality (covered by the develop-synthesis suite), nor persistence/frontmatter mechanics (covered by the behavior tests in the manifest).

**Grader instructions:** Read only three inputs — the produced `educator-evaluation.md` artifact, this rubric, and the fixture idea (`Fixtures/Ideas/accommodations-on-classroom-checks.md`). For each signal, return PASS/FAIL and quote the artifact line(s) that justify the verdict. A signal with no quotable supporting line is a FAIL. Report per-signal; the persona passes the research-quality bar only if all signals PASS.

---

## Signal 1 — Classroom-constrained adoption grounding

**Definition:** Adoption Realism / Adoption Barriers are grounded in concrete classroom constraints — the existing tool stack, specific time windows in the teaching day/year, or a stated friction level — not abstractions. Derived from agent Quality Standards ("Specific over general. 'During the 10-minute window between second and third period' not 'when teachers have time'"), Evaluation Framework dim 2 (Adoption Realism: low/medium/high friction) and dim 3 (Workflow Integration), and the persona's concrete constraints (150 students, 45-minute periods, an existing daily tool stack).

**PASS when:** Adoption Barriers cite at least one concrete constraint — the specific tools teachers already use, a named time window in the day/week/year, or an explicit friction level with the workflow reason behind it.

**FAIL patterns:**

- "Teachers might find it hard to adopt" with no classroom mechanics.
- Generic change-management language ("requires buy-in," "adoption takes time").
- Friction asserted without naming the competing workflow or tool it displaces.

**Evidence requirement:** Quote the Adoption Barriers line(s) naming the concrete constraint (tool stack, time window, or workflow friction).

---

## Signal 2 — Named pain points from practice (felt vs. imagined)

**Definition:** Pain Point Analysis distinguishes real, daily-felt teacher pain from institution-felt or imagined pain, described from lived classroom practice. Derived from Evaluation Framework dim 1 (Pain Point Validity: "pain the teacher feels daily, pain felt occasionally, pain the institution feels but teachers don't, and pain that's imagined entirely") and agent Quality Standards ("Educator voice, not product voice").

**PASS when:** The analysis names a specific pain AND classifies whose pain it is (teacher-felt daily vs. institution/buyer-felt vs. latent/imagined), grounded in a described classroom scenario rather than an abstract problem statement.

**FAIL patterns:**

- Asserts a pain without the whose-pain distinction (treats a product-team-imagined or institution-only pain as daily teacher pain).
- Product voice ("users experience friction") instead of educator voice.
- No lived detail — no scenario a teacher would recognize.

**Evidence requirement:** Quote the Pain Point Analysis line(s) that name the pain and classify whose pain it is.

---

## Signal 3 — Champion-vs-skeptic scenarios

**Definition:** Both a skeptic's genuine eye-roll objection and a champion's specific excitement moment are present, each concrete (a scenario, not a feature list). Derived from Evaluation Framework dim 4 (The Skeptic's Objection: "the teacher who's seen 15 revolutionary tools come and go") and dim 5 (The Champion's Argument: "a specific moment... Not a feature list — a moment. If no genuine excitement moment exists, say so honestly"), and the artifact's "What Would Make Educators Skeptical" / "Champions" sections.

**PASS when:** Both sections are present; the skeptic voices a real objection an experienced educator would raise (or the artifact honestly states no excitement moment exists, if that is the finding), and the champion describes a specific moment/scenario rather than listing features.

**FAIL patterns:**

- One side missing or reduced to a single vague sentence.
- Champion section is a feature list ("teachers would like X, Y, Z") rather than a described moment.
- Skeptic objection is a strawman or softened to avoid harshness.

**Evidence requirement:** Quote one concrete line from the skeptic section and one from the champion section.

---

## Signal 4 — Pedagogical-soundness / student-outcome judgment

**Definition:** The evaluation makes an explicit call on whether the idea serves student learning, and flags institution-benefit-only cases. Derived from agent Quality Standards ("Student outcomes matter. If this helps institutions but not students, flag it explicitly. 'Great for admin dashboards, invisible to the kid struggling with fractions.'") and the persona's core orientation ("Cares about whether students actually learn, not whether dashboards look impressive").

**PASS when:** The artifact makes an explicit judgment about student-outcome / pedagogical value — either arguing how it reaches the student, or flagging that the benefit accrues to the institution and is invisible/indirect to the student.

**FAIL patterns:**

- Evaluates only convenience/efficiency/admin value with no student-learning lens.
- Assumes institutional benefit equals student benefit without examining it.
- No pedagogical judgment anywhere in the artifact.

**Evidence requirement:** Quote the line making the student-outcome / pedagogical-value call.

---

## Signal 5 — Barrier honesty (what would make a teacher NOT adopt)

**Definition:** The Adoption Assessment verdict is honest (harsh where warranted, not encouraging by default) and names concrete conditions under which teachers would reject the idea. Derived from agent Quality Standards ("Honest over encouraging. Killed at Stage 2 saves months of wasted effort. A harsh evaluation is more valuable than a polite one."), Evaluation Framework dim 2, and the artifact's Adoption Assessment verdict + Suggested Refinements.

**PASS when:** An explicit Adoption Assessment verdict (High/Medium/Low) is stated AND at least one concrete non-adoption condition is named (for example: extra steps per student, time the school day does not have, loss of teacher discretion).

**FAIL patterns:**

- Uniformly encouraging tone with no non-adoption condition named.
- Verdict omitted or left implicit.
- Rosy verdict unjustified by the barriers the artifact itself lists.

**Evidence requirement:** Quote the Adoption Assessment verdict and one concrete non-adoption condition.

---

## Signal 6 — Segment sensitivity (K-12 vs. higher ed)

**Definition:** The evaluation calibrates to the relevant segment(s) and does not silently generalize across K-12 and higher ed. Derived from agent Quality Standards ("Segment sensitivity. K-12 and higher ed are different worlds. Never generalize across segments without noting the differences.") and SKILL Step 2 domain calibration (K-12 / higher ed / platform-downstream).

**PASS when:** The artifact states its segment calibration and, where both segments apply, notes where they diverge — or explicitly scopes to one segment with a stated reason (e.g., higher-ed applicability unvalidated / out of scope).

**FAIL patterns:**

- Blends K-12 and higher ed indiscriminately with no calibration stated.
- Imports higher-ed assumptions into a K-12-scoped idea (or vice versa) without noting the difference.
- No segment framing at all.

**Evidence requirement:** Quote the domain-calibration line and any statement scoping or differentiating the segments.
