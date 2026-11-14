# Rubric: tam-estimate research-quality signals

**Provenance:** Signal set authored 2026-07-07, grounded in `plugins/incubator/skills/tam-estimate/SKILL.md` (Execution Flow Steps 3-5, artifact template) and `plugins/incubator/agents/tam-estimate.md` (Quality Standards, SOM cap, divergent analyst mode).

**What this rubric is for:** The named, checkable regression bar for "did tam-estimate's *research quality* hold?" It is distinct from the suite's mode-handling behavior tests (idea/ad-hoc/fail-closed). It gates Phase 2 model changes and serves as a thesis-test lens. Every signal derives from what the persona's own standards already demand — no outside frameworks are imported.

**Scope note:** These signals check the produced artifact's analytical quality. They do NOT check general develop-synthesis card quality (covered by the develop-synthesis suite), nor persistence/frontmatter mechanics (covered by the behavior tests in the manifest).

**Grader instructions:** Read only three inputs — the produced `tam-estimate.md` artifact, this rubric, and the fixture idea (`Fixtures/Ideas/accommodations-on-classroom-checks.md`). For each signal, return PASS/FAIL and quote the artifact line(s) that justify the verdict. A signal with no quotable supporting line is a FAIL. Report per-signal; the persona passes the research-quality bar only if all signals PASS.

---

## Signal 1 — Dual-path methodology present

**Definition:** Both a top-down estimate (broad market narrowed by a filter chain) and an independent bottom-up estimate (buyer count x spend per buyer) are constructed, each producing its own TAM. Derived from SKILL Step 3 (Top-Down Estimation) and Step 4 (Bottom-Up Estimation), and the artifact's Top-Down Analysis + Bottom-Up Analysis sections.

**PASS when:** A distinct Top-Down analysis (starting market -> successive filters -> TAM) AND a distinct Bottom-Up analysis (buyer count x spend per buyer -> TAM) are both present, each yielding a separately stated TAM figure.

**FAIL patterns:**

- Only one methodology present (top-down only, or bottom-up only).
- A "bottom-up" that merely restates the top-down number without a buyer-count build.
- Missing filter chain, or a buyer count with no per-buyer spend (or vice versa).

**Evidence requirement:** Quote one top-down filter-chain row (filter -> resulting market -> source) and one bottom-up build line (buyer count and/or spend-per-buyer feeding a TAM).

---

## Signal 2 — Sourced inputs (named source + number + date)

**Definition:** Every material figure carries a named source, and where recency matters a publication date; nothing older than ~2 years is presented as current without a flag. Derived from agent Quality Standards ("Every data point cited. Source name, URL, and publication date for every number used in estimation." and "Recency matters. Prefer data from the last 2 years. Flag anything older.") and the artifact's Sources table.

**PASS when:** The top-down market anchor and the bottom-up buyer counts each cite a named source (analyst firm, NCES, government data, comparable-company revenue, etc.), a Sources table lists source + URL + date, and any figure older than ~2 years is flagged.

**FAIL patterns:**

- Unsourced point estimates ("the market is roughly $X") with no attribution.
- "Industry estimates suggest..." with no named source.
- No dates on time-sensitive figures; stale figures used as current without a flag.

**Evidence requirement:** Quote one Sources-table row (source + date) and one in-body figure that cites its named source.

---

## Signal 3 — SAM/SOM narrowing with stated assumptions + SOM cap

**Definition:** TAM is narrowed to SAM then SOM via explicit, stated filters, and SOM is capped to the organization's actual per-segment market position. Derived from SKILL Step 3 (SAM = "what your organization could realistically compete for"; SOM = "realistic capture given current market position"), Step 5 SOM cap, and agent SOM cap rule ("SOM must be capped relative to its actual market position... use its per-segment shares as the ceiling").

**PASS when:** A SAM filter is stated (serviceable subset + the reason it is narrower than TAM) AND SOM applies an explicit market-position/penetration cap tied to the organization (a stated share or penetration percentage), not an arbitrary fraction.

**FAIL patterns:**

- SAM equals TAM, or SOM stated with no cap rationale.
- SOM implying an implausible share with no penetration basis.
- Narrowing percentages with no stated assumption behind them.

**Evidence requirement:** Quote the SAM narrowing rationale and the SOM cap line (with its penetration/share basis).

---

## Signal 4 — Reconciliation between the two paths

**Definition:** The top-down and bottom-up results are explicitly compared; convergence or divergence is stated; and divergence beyond ~2x is investigated and resolved (or explained). Derived from SKILL Step 5 Reconciliation ("Compare... If within 2x... converge... If >2x divergence: investigate why") and the artifact's Reconciliation section.

**PASS when:** The artifact explicitly compares the two TAMs, states whether they converge or diverge (within/over 2x), resolves or explains any divergence, and lands on a stated final band/center of mass.

**FAIL patterns:**

- Two TAM numbers presented with no comparison between them.
- Divergence noted but never investigated or resolved.
- No final reconciled band stated.

**Evidence requirement:** Quote the convergence/divergence statement and the resolution/final-band line.

---

## Signal 5 — Conservative bias + sensitivity caveat

**Definition:** Estimates are banded conservative/moderate/aggressive with the conservative case leaning genuinely low, and a sensitivity analysis identifies the highest-impact variables and their swing. Derived from agent Quality Standards ("Conservative bias. When uncertain, estimate lower.") and SKILL Step 5 Sensitivity analysis ("Identify the 2-3 highest-impact variables... Show +/- 25% range impact") + the artifact's Sensitivity Analysis table.

**PASS when:** A three-scenario band is present with conservative < moderate < aggressive AND a sensitivity analysis names the 2-3 variables that most move the estimate and shows their +/- impact.

**FAIL patterns:**

- A single point estimate with no scenario band.
- Band present but no sensitivity analysis.
- Aggressive-leaning default (headline number is the optimistic case) contradicting conservative bias.

**Evidence requirement:** Quote the scenario band (conservative/moderate/aggressive figures) and one sensitivity-analysis row.

---

## Signal 6 — No-fabrication honesty (estimated vs. sourced)

**Definition:** The artifact explicitly separates figures that are sourced from figures that are estimated/triangulated, and avoids invented precision. Derived from agent Quality Standards ("No fabrication. If a number cannot be sourced, say so. 'Estimated based on [methodology]' is acceptable. Invented precision is not.") and the artifact's Limitations section.

**PASS when:** A Limitations (or equivalent) passage names which figures are inferred/triangulated/estimated versus sourced, and flags unvalidated inputs — so the reader knows the confidence texture behind the numbers.

**FAIL patterns:**

- All numbers presented with equal, false confidence; no Limitations passage.
- Precise figures (e.g., a specific ACV) presented as fact when the artifact elsewhere shows they were inferred.
- No acknowledgment of data gaps that the analysis clearly depends on.

**Evidence requirement:** Quote the Limitations line(s) distinguishing an estimated/triangulated figure from a sourced one.
