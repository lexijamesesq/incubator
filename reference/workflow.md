# Workflow

> One section of the `incubator-reference.md` reference index — see it for the full section map.

## Intake

Seeds arrive from the router as rows in the Ideas database, with their fields set and the Original Capture in the body. The router does not interpret the capture — /refine-seed handles that before /develop. Classification and routing behavior are the router's own; its spec is not part of this repo.

## Refining a Seed (Stage 1 prep)

**Trigger:** Human says "refine-seed [idea name]" or equivalent. Run before /develop.

**What it does:** Interprets the raw seed's intent — determines whether the idea is a capability gap or an experience improvement, drafts header fields (core insight, problem, who cares, strategic connection), surfaces related ideas for potential consolidation, and aligns with the human before /develop runs. This is where ambiguous seeds get clarified so the synthesis agent has clean inputs. When the human approves a merge of two seeds, the secondary's row is set to `Stage` `archived` and drops out of the seed list (`reference/architecture.md`, Archive Conventions).

## Developing an Idea (Stage 1→2)

**Trigger:** Human says "develop [idea name]" or equivalent. Seed should be refined first via /refine-seed.

**Architecture:** Orchestrator + synthesis agent. The /develop skill is an orchestrator that handles research and procedure. The develop-synthesis agent (`.claude/agents/develop-synthesis.md`) handles strategic judgment in an isolated context.

**Orchestrator flow:**

1. Read the seed row and verify refinement (structured fields present)
2. Research autonomously across three streams:
   - **Stream A:** Strategy docs, NPS data, customer evidence
   - **Stream B:** Market intelligence, competitive landscape, web research
   - **Stream C:** Cross-domain discovery via /cross-domain (JPD query)
3. Build a synthesis handoff consolidating all research (a `synthesis-handoff` row in the Research database, related to the idea)
4. Dispatch to the develop-synthesis agent (Opus, isolated context) to produce the TL;DR card
5. Post-synthesis: buildable surface check, theme governance, title revision, artifact critic, self-critique
6. Present completed TL;DR for human review

## Drafting (Stage 2→3)

**Trigger:** Human says "draft [idea name]" and specifies output format (strategy doc or brief).

**Agent behavior:**

1. Read idea card (TL;DR) and all attached research
2. Evaluate sufficiency: enough context to draft every template section?
3. If gaps exist: identify what's missing, propose how to fill (research, human input, internal docs)
4. If sufficient: create the output document as a row in the Outputs database, named `{idea-name}-{format}` and related to the idea, using the appropriate template (the page `template_strategy_doc` or `template_product_brief` names)
5. Self-critique against validation checklist before presenting
6. Update the idea row's fields: `Stage` `drafting`, `Updated` (the new Outputs row is already in its `Outputs` relation) — do NOT modify idea card body

## Refining (Stage 3→4)

**Trigger:** Automatic after Stage 3 draft is presented.

**Behavior:** Works on the output document (not the idea card). Follows the collaboration protocol from the approach methodology (the page the `approach` configuration key names):

1. Establish north star alignment on the draft
2. Iterate section-by-section based on human feedback
3. Self-critique between iterations
4. Validate voice against persona guide
5. Check strategic connections for realism (not overstated)
6. As many feedback loops as needed — quality over speed
7. If direction shifts significantly, update the idea card to reflect new framing
