# Rubric: edtech-sme research-quality signals

**Provenance:** Signal set authored 2026-07-07, grounded in `plugins/incubator/skills/edtech-sme/SKILL.md` (Execution Flow, Research quality standards, artifact template) and `plugins/incubator/agents/edtech-sme.md` (Quality Standards, Evaluation Framework).

**What this rubric is for:** The named, checkable regression bar for "did edtech-sme's *research quality* hold?" It is distinct from the suite's mode-handling behavior tests (idea/ad-hoc/fail-closed). It gates Phase 2 model changes and serves as a thesis-test lens. Every signal derives from what the persona's own standards already demand — no outside frameworks are imported.

**Scope note:** These signals check the produced artifact's analytical quality. They do NOT check general develop-synthesis card quality (covered by the develop-synthesis suite), nor persistence/frontmatter mechanics (covered by the behavior tests in the manifest).

**Grader instructions:** Read only three inputs — the produced `edtech-market-analysis.md` artifact, this rubric, and the fixture idea (`Fixtures/Ideas/accommodations-on-classroom-checks.md`). For each signal, return PASS/FAIL and quote the artifact line(s) that justify the verdict. A signal with no quotable supporting line is a FAIL. Report per-signal; the persona passes the research-quality bar only if all signals PASS.

---

## Signal 1 — Named-competitor differentiation

**Definition:** The Competitive Positioning section names specific real companies (and their products/capabilities), each carried to an explicit `Differentiation / Parity / Behind` verdict. Derived from agent Quality Standards ("Name competitors, cite products, reference real dynamics. No generic 'competitors in the space' — name them.") and SKILL Step 4 ("build a competitor comparison table with specific companies, their relevant capabilities, and how your organization would compare").

**PASS when:** The positioning table (or equivalent prose) names at least three real, identifiable competitors, each with a named capability/product AND a comparison verdict (Differentiation / Parity / Behind / a stated adjacency).

**FAIL patterns:**

- Generic references — "competitors in the space," "several established players" — with no company names.
- Named companies but no per-competitor comparison verdict (no Differentiation/Parity/Behind call).
- Capability column blank or vague ("does assessment stuff") rather than a specific product/capability.

**Evidence requirement:** Quote at least two competitor rows showing company + capability + comparison verdict.

---

## Signal 2 — Recency-stamped market intelligence

**Definition:** Material competitive/market claims carry explicit dates or recency markers, and any knowledge older than 18 months is flagged. Derived from agent Quality Standards ("Current data. Flag any knowledge more than 18 months old.") and SKILL Step 3 Research quality standards ("Flag any knowledge that is more than 18 months old").

**PASS when:** Multiple competitive or regulatory claims carry an explicit date or recency signal (e.g., a month/year on an acquisition, launch, standard release, or regulatory transition), and any figure/claim more than ~18 months old is explicitly flagged as such.

**FAIL patterns:**

- No dates anywhere — undated "competitors are bundling" / "the market is consolidating" assertions.
- Stale data presented as current with no age flag.
- A single throwaway year with the rest of the analysis undated.

**Evidence requirement:** Quote at least two dated/recency-stamped claims (and, if any old data is used, the line that flags it).

---

## Signal 3 — Buyer / procurement dynamics named

**Definition:** Market Fit and Go-to-Market are buyer-centric — they identify who actually buys, the procurement/funding mechanics, and ground demand in willingness to pay rather than product excitement. Derived from agent Quality Standards ("Buyer-centric. Market fit = willingness to pay, not product excitement. Think like a procurement officer."), Evaluation Framework dims 1 & 4, and the SKILL artifact's Market Fit + Go-to-Market sections.

**PASS when:** The artifact identifies the specific buyer (role/level, e.g., district administrator vs. classroom teacher), names at least one concrete procurement/funding dynamic (contract structure, funding source such as Title I/ESSER, sales cycle), and frames market fit in willingness-to-pay terms.

**FAIL patterns:**

- Product-excitement framing ("teachers would love this," "users would benefit") with no buyer or procurement lens.
- No identified buyer, or the buyer conflated with the end user when they differ.
- Market fit asserted with no willingness-to-pay evidence.

**Evidence requirement:** Quote the Market Fit and/or Go-to-Market line(s) naming the buyer and a procurement/funding dynamic.

---

## Signal 4 — Technology-risk & regulatory grounding

**Definition:** Technology Risk is rated Low/Medium/High and substantiated with institutional-deployment maturity plus at least one concrete integration, interoperability-standard, or regulatory constraint. Derived from Evaluation Framework dim 3 (Technology Risk: "maturity for institutional deployment, integration requirements... accessibility compliance"), SKILL Step 4 ("rate as Low / Medium / High... assess the gap between current capability and institutional deployment readiness"), and the artifact's Technology Risk section.

**PASS when:** An explicit Low/Med/High rating appears AND is justified by at least one named integration/standard/regulatory reality (e.g., QTI/LTI, OneRoster/Ed-Fi, a data-privacy statute, an accessibility requirement) tied to institutional deployment readiness.

**FAIL patterns:**

- Rating stated with no substantiation ("Technology Risk: Medium." then nothing concrete).
- Hand-waved maturity ("the tech is proven") with no named standard, integration, or regulatory constraint.
- Generic risk language with no institutional-deployment lens.

**Evidence requirement:** Quote the rating line plus the sentence naming the specific standard/integration/regulatory constraint.

---

## Signal 5 — Competitive-window timing call

**Definition:** Strategic Timing makes an explicit, non-hedged market-window judgment (market moving toward vs. away; first-mover vs. fast-follower) grounded in specific external forcing signals. Derived from SKILL Step 5 ("Is the market moving toward this idea or away... first-mover advantage, or is fast-follower safer... Specific timing signals: funding cycles, regulatory deadlines, competitor roadmap signals, technology maturity curves") and agent Quality Standards ("No hedging").

**PASS when:** The section states a directional window call AND cites at least one specific timing signal (a dated regulatory forcing function, competitor roadmap move, funding cycle, or technology-maturity inflection) AND takes a first-mover/fast-follower stance (explicit or clearly implied by the urgency framing).

**FAIL patterns:**

- Hedged non-calls — "the market could potentially be moving toward..." with no commitment.
- Timing asserted with no specific signal behind it.
- No window judgment at all (section describes the market but never says whether the clock favors acting now).

**Evidence requirement:** Quote the directional call and the specific timing signal supporting it.

---

## Signal 6 — Honest positioning + ARR connection

**Definition:** The positioning narrative and Opportunity Signal Strength give an honest self-assessment (concede gaps / name where the org is "Behind" when true) and connect the opportunity to the revenue mechanism (MAU x ARPU = ARR — new ARR, retention, or expansion). Derived from agent Quality Standards ("Honest. If the company is behind a competitor with a 2-year head start, say so." and "Connect to MAU x ARPU = ARR. Every market assessment should connect back to how it affects active usage and revenue per user.") and the artifact's Positioning narrative + Opportunity Signal Strength sections.

**PASS when:** The positioning narrative honestly states the org's standing (including "behind" where the evidence supports it, not only favorable framing) AND the opportunity/GTM analysis connects to a revenue mechanism (new ARR vs. retention/expansion, active-usage impact).

**FAIL patterns:**

- Uniformly rosy positioning that never concedes a competitive gap that the competitor table implies.
- Opportunity strength asserted with no revenue/ARR logic.
- Revenue mentioned but disconnected from the actual competitive standing (e.g., claims large new ARR while the table shows the org two years behind incumbents).

**Evidence requirement:** Quote the honest-standing line from the positioning narrative and the ARR/revenue-mechanism line from Opportunity Signal Strength (or GTM).
