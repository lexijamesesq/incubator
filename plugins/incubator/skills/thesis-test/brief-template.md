# Thesis Brief Template

Bundled with `/thesis-test`, loaded by Step 1 when a brief must be co-drafted. The brief is the committed strategic position(s) under test. It is **human-owned** — the human states every claim; the skill helps structure it and presses for falsifiable break conditions.

**Hybrid contract:** the *structure* below is required; the *reasoning within each section* is freeform. Fill every required section. `/thesis-test` refuses to run the lenses until the break-condition table has full (thesis × lens) coverage and the learning-outcome row is populated.

---

## Required sections

### 0. Givens (not under test)

Constraints, decided destinations, and validated facts the run treats as fixed — the frame the fight happens inside; rivals form only in the contested space outside them. Each given carries a one-line warrant — `validated-by-{X}` / `decided-by-{Y}` / `out-of-scope-{Z}` — and the co-draft asks of each once: **"why is this fixed, not contested?"** Lenses do not verdict givens, but the flag rule holds: evidence that squarely contradicts one is flagged (`GIVEN-CONTESTED`), never suppressed — a broken frame outranks a polite fight inside it.

### 1. Strategic Claim(s)

One or more theses (1..N). Each is a **committed position with reasoning — a claim, not a question.** "Family messaging should be sold to districts as a product of its own, because the office that buys it is not the office that buys the learning platform" is a thesis. "Should we sell family messaging separately?" is not. For each thesis give:

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

- **Audience:** who reads the output (e.g., "a chief product officer who already favours one of the rivals").
- **Persona file:** the voice/style file for that audience, if one exists. **If none exists, say so here as a gap — do NOT default to a generic register.** Generic register is the failure mode, not the fallback.
- **Artifact shape:** e.g., narrative-conviction vs. status-report vs. analytical brief; length constraint.
- **Defensibility bar:** what the surviving position must survive next (leadership pitch, board paper, JPD push) — the synthesis writes toward it. Check it against the audience: a bar naming a later gate than the audience implies (audience "the board" but bar "JPD push") is incoherent — reconcile before writing.

### 5. Reuse / Re-Run Partition Pointer (card-mode)

For a card-mode run, name the idea's prior research artifacts (the rows in the idea row's Research relation) and any up-front intuition about which slices are thesis-independent (carry forward) vs. thesis-dependent (re-run). This seeds Step 2 — the skill still applies the "would this hold under any plausible thesis?" test per slice; this pointer is a starting hint, not the decision. Omit for subject-mode.

---

## Worked-example skeleton

Three rivals for one capability, each leading with a different wedge to a different buyer: a headline number, an hour given back, a service. Placeholders only — no organization, product, or competitor names. Replace every `{…}`.

```text
# Thesis brief: {Subject}

**Status:** Hypotheses under test. Lenses should validate, challenge, or break these. Do not treat as established truth.

## Thesis A: {The headline-number play}
**Thesis:** {Lead with the one figure the customer's leadership already reports upward. Move that figure and the product is bought from the top, whatever the people below think of it.}
**Why now:** {the figure has just become public, or has just been tied to funding}.

| Lens | Break condition |
|------|-----------------|
| edtech-sme | If every competitor already claims to move the same figure, the claim separates nobody — the thesis weakens. |
| tam-estimate | If the leader who answers for the figure holds no technology budget, the person persuaded is not the person who pays — the thesis weakens. |
| educator-sme | If the figure only moves when practitioners record more, the number improves and the practice does not — the thesis breaks. |
| Learning-outcome (educator-sme) | {configured phrasing — does the wedge reach a learning/product surface, or only a buyer pain?} |

## Thesis B: {The hour-back play}
**Thesis:** {Lead with the weekly chore this removes. The people who do it are already users, and a product they would miss is one their employer renews.}
**Why now:** {a renewal cycle in which the chore came up unprompted}.

| Lens | Break condition |
|------|-----------------|
| edtech-sme | If no buyer scores practitioner time in a tender, the benefit wins users and no contract — the thesis weakens. |
| tam-estimate | If it ships inside the existing licence, the only revenue is renewal, and the renewal rate has to move for it to count — the thesis weakens. |
| educator-sme | If practitioners use the chore to get to know the people in front of them, removing it takes away something they value — the thesis breaks. |
| Learning-outcome (educator-sme) | {configured phrasing}. |

## Thesis C: {The service play}
**Thesis:** {Lead with our people. Sell setup and training delivered in person, and let the product follow the relationship those visits build.}
**Why now:** {customers are asking for help that the product alone does not give them}.

| Lens | Break condition |
|------|-----------------|
| edtech-sme | If competitors include setup at no charge, a paid service reads as a product that is hard to use — the thesis weakens. |
| tam-estimate | If every new customer needs more of our staff, revenue grows only as fast as hiring does — the thesis breaks. |
| educator-sme | If practitioners count training as time taken from them, their first meeting with us is one they resent — the thesis weakens. |
| Learning-outcome (educator-sme) | {configured phrasing}. |

## Register declaration
- Audience: {e.g., a leadership group choosing between the three}
- Persona file: {path, or "none — flagged as a gap"}
- Artifact shape: {e.g., stack-rank with recomposition; conviction register; ≤2 pages}

## Reuse / re-run partition pointer (card-mode)
- Prior artifacts: {the idea's research rows, by Research type}
- Likely reusable: {e.g., competitor universe, cross-domain signals}
- Likely re-run: {e.g., positioning under the committed thesis, market definition}
```
