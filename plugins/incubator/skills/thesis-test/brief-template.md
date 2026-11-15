# Thesis Brief Template

Bundled with `/thesis-test`, loaded by Step 1 when a brief must be co-drafted. The brief is the committed strategic position(s) under test. It is **human-owned** — the human states every claim; the skill helps structure it and presses for falsifiable break conditions.

**Hybrid contract:** the *structure* below is required; the *reasoning within each section* is freeform. Fill every required section. `/thesis-test` refuses to run the lenses until the break-condition table has full (thesis × lens) coverage and the learning-outcome row is populated.

---

## Required sections

### 0. Givens (not under test)

Constraints, decided destinations, and validated facts the run treats as fixed — the frame the fight happens inside; rivals form only in the contested space outside them. Each given carries a one-line warrant — `validated-by-{X}` / `decided-by-{Y}` / `out-of-scope-{Z}` — and the co-draft asks of each once: **"why is this fixed, not contested?"** Lenses do not verdict givens, but the flag rule holds: evidence that squarely contradicts one is flagged (`GIVEN-CONTESTED`), never suppressed — a broken frame outranks a polite fight inside it.

### 1. Strategic Claim(s)

One or more theses (1..N). Each is a **committed position with reasoning — a claim, not a question.** "The premium offering is an integrated evidence platform because the integration gap is the pain" is a thesis. "Should we build an evidence platform?" is not. For each thesis give:

- **Thesis:** the position, stated as a conviction.
- **Why now:** the timing/urgency signals that make it live.
- (optional) **What it combines:** if the thesis fuses several moves, name them.

Competing theses are encouraged — testing 2–5 rival visions against each other is the strongest use of the skill (see the worked-example skeleton). **Distinguishability:** rivals must differ materially in wedge, buyer, or surface — two variants of one position are one thesis.

### 2. Per-(Thesis × Lens) Break-Condition Table

The heart of the brief. For EVERY thesis, for EVERY lens, a falsifiable break condition: **"if X, this thesis weakens/breaks."** Not a question, not an enrichment ask — a condition whose truth would mark the thesis down. Conditions are derived per `attack-patterns.md` §C (must-hold conditions → fragility-rank → derive) and cite palette attacks by name where one applies. Coverage is enforced: a missing cell blocks the run.

Repeat this block per thesis:

```text
#### Thesis {A}: {short name}

| Lens | Break condition (if X, this thesis weakens/breaks) |
|------|-----------------------------------------------------|
| edtech-sme | If {competitor/market condition}, then {thesis} {weakens/breaks} because {why}. |
| tam-estimate | If {sizing/economics condition}, then {thesis} {weakens/breaks} because {why}. |
| educator-sme | If {adoption/classroom-reality condition}, then {thesis} {weakens/breaks} because {why}. |
| Learning-outcome (educator-sme) | {REQUIRED — see §3} |
```

### 3. Learning-Outcome Break Condition (REQUIRED)

A permanent break condition on every thesis, tested by educator-sme's pass. Pre-fill this row from the phrasing the Configuration page gives as `incubator.learning_outcome_break_condition` (installation-specific — the skill and this template carry only the key reference, never the literal value).

Its shape: **does the wedge land on a learning/product surface, or only on a buyer pain through a procurement motion?** A thesis can pass every market, sizing, and adoption test and still fail this one — procurement-coherent but product-incoherent. Put the configured phrasing in the "Learning-outcome" row of every thesis's table.

### 4. Register Declaration

The synthesis is an audience-shaped artifact; declare its register before it is written:

- **Audience:** who reads the output (e.g., "CPO who has already bought the platform play").
- **Persona file:** the voice/style file for that audience, if one exists. **If none exists, say so here as a gap — do NOT default to a generic register.** Generic register is the failure mode, not the fallback.
- **Artifact shape:** e.g., narrative-conviction vs. status-report vs. analytical brief; length constraint.
- **Defensibility bar:** what the surviving position must survive next (leadership pitch, EC submission, JPD push) — the synthesis writes toward it. Check it against the audience: a bar naming a later gate than the audience implies (audience "CPO/EC" but bar "JPD push") is incoherent — reconcile before writing.

### 5. Reuse / Re-Run Partition Pointer (card-mode)

For a card-mode run, name the idea's prior research artifacts (the rows in the idea row's Research relation) and any up-front intuition about which slices are thesis-independent (carry forward) vs. thesis-dependent (re-run). This seeds Step 2 — the skill still applies the "would this hold under any plausible thesis?" test per slice; this pointer is a starting hint, not the decision. Omit for subject-mode.

---

## Worked-example skeleton (abstracted)

Shape drawn from multi-thesis product-vision stress-tests. Placeholders only — no organization, product, or competitor names. Replace every `{…}`.

```text
# Thesis brief: {Subject}

**Status:** Hypotheses under test. Lenses should validate, challenge, or break these. Do not treat as established truth.

## Thesis A: {The horizontal-capability play}
**Thesis:** {The offering is a general-purpose engine for the whole lifecycle; the value is the connected lifecycle no competitor owns end-to-end.}
**Why now:** {mandate window + no incumbent owns the full lifecycle}.

| Lens | Break condition |
|------|-----------------|
| edtech-sme | If there is no procurement category for a "general-purpose {X}," it has no buyer and no home in an RFP — the thesis breaks. |
| tam-estimate | If verticals dominate the spend, the horizontal SOM is the residual, not the core — the thesis weakens. |
| educator-sme | If a general-purpose tool can't speak the practitioner's discipline, adoption stalls — the thesis weakens. |
| Learning-outcome (educator-sme) | {configured phrasing — does the wedge reach a learning/product surface, or only a buyer pain?} |

## Thesis B: {The vertical-shell play}
**Thesis:** {The offering is a shell that houses vertical-specific modules; the value is the connective tissue across silos.}
**Why now:** {simultaneous accreditation windows across verticals}.

| Lens | Break condition |
|------|-----------------|
| edtech-sme | If entrenched vertical incumbents can't be displaced (multi-year contracts, deep switching cost), the shell must partner not replace — the thesis weakens. |
| tam-estimate | If integration layers can't command premium pricing (absorbed into base platform expectations), the monetization breaks. |
| educator-sme | If credible multi-vertical modules can't ship at launch (shallow coverage detected by program directors), the sequencing breaks. |
| Learning-outcome (educator-sme) | {configured phrasing}. |

## Thesis C: {The single-vertical-beachhead play}
**Thesis:** {Pick the highest-ARPU vertical; own it; expand later.}
**Why now:** {a specific accreditation driver creating urgency in that vertical}.

| Lens | Break condition |
|------|-----------------|
| edtech-sme | If the incumbent is free-to-institution and workflow-embedded, switching cost defeats entry — the thesis weakens. |
| tam-estimate | If the vertical TAM is too thin for a standalone investment, it only makes sense as a module — the thesis weakens. |
| educator-sme | If the buyer's workflow needs operational logistics the product won't own, it's an add-on not a replacement — the thesis breaks. |
| Learning-outcome (educator-sme) | {configured phrasing}. |

## Register declaration
- Audience: {e.g., executive committee evaluating an acid test}
- Persona file: {path, or "none — flagged as a gap"}
- Artifact shape: {e.g., stack-rank with recomposition; conviction register; ≤2 pages}

## Reuse / re-run partition pointer (card-mode)
- Prior artifacts: {the idea's research rows, by Research type}
- Likely reusable: {e.g., competitor universe, cross-domain signals}
- Likely re-run: {e.g., positioning under the committed thesis, market definition}
```
