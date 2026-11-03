# Incubator Reference — Section Index

Reference material for Incubator stage work, split into section-scoped files under `reference/` so skills load only the section they need instead of the whole document. Each row below maps a section to its file. For project state, intake, session protocol, and system overview, see `.claude/instance.md`. On 2026-07-07 this document was reduced from a ~31K-char monolith to this index; the section files carry the content verbatim.

**How to use:** Load the specific `reference/{file}.md` your task needs — do not load this whole set. Each pipeline skill names the sections it requires in its own instructions.

| Section | File | Contents |
| --------- | ------ | ---------- |
| Stage Model | `reference/stage-model.md` | The 0→5 stage table: name, what happens, who drives, entry/exit criteria per stage. |
| Architecture | `reference/architecture.md` | Two-track model (idea cards + output docs), card update rules, consolidation points, cross-stage detection, merge mechanics, archive conventions. |
| Frontmatter Schema | `reference/frontmatter-schema.md` | The idea-card YAML frontmatter schema, impact-dimension rationale, TAM/related-ideas rules. |
| Templates | `reference/templates.md` | **Seed Template** (Stage 1), TL;DR Template (Stage 2), and Output Templates (strategy doc / product brief). |
| Workflow | `reference/workflow.md` | Per-stage process: intake, refine-seed, develop (orchestrator + synthesis agent), draft, refine. |
| Voice & Output Standards | `reference/voice-and-output-standards.md` | Persona pointer and the "Designers speaking Design" exit test. |
| Research Protocol | `reference/research-protocol.md` | Strategy-doc queries, market intelligence, cross-domain discovery, when to pause and ask. |
| Shared Research | `reference/shared-research.md` | Snowflake `research_findings` table: topics, capture heuristic, governance, TTL reference, citation + /draft verification rules. |
| Initiative Schema | `reference/initiative-schema.md` | Initiative frontmatter, child-to-parent reference, initiative stage model, output-format heuristic, body template. |
| JPD Integration | `reference/jpd-integration.md` | Push purpose, JPD idea template alignment, push criteria, sync-tracking frontmatter, sync-back policy. |
| Skill Conventions: Vault Access | `reference/skill-conventions-vault-access.md` | Rule that vault-touching skills/agents declare the native tools they use; per-operation tool table and the CLI move rule. |

## Seed intake contract (router reads this)

The upstream router conforms to the Incubator's seed contract. The two sections that define it:

- **Frontmatter Schema** → `reference/frontmatter-schema.md`
- **Seed Template** → `reference/templates.md` (`### Seed Template (Stage 1)`)

A reader arriving from "incubator-reference.md (sections: Frontmatter Schema, Seed Template)" routes to those two files in one hop.
