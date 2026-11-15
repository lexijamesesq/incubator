# Initiative Schema

> One section of the `incubator-reference.md` reference index — see it for the full section map.

Initiatives are structural parents — strategic containers that hold multiple related ideas under a unifying narrative. They are distinct from ideas: initiatives frame the strategic argument, ideas are the discrete proposals within it.

**Examples:**

- "Authentic Assessment for BTS '27" holds 8 child ideas (grading, rubric design, scalability, etc.)
- "Platform AI Intelligence Layer" holds ideas for intelligence models that compose into shared infrastructure

## Initiative Frontmatter

An initiative is a row in the Ideas database whose `Type` is `initiative`. Each key below is a field of that row: `organizing-question` and `strategic-narrative` are the text fields `Organizing question` and `Strategic narrative`, and `child-ideas` is the `Child ideas` relation to other Ideas rows.

```yaml
---
type: incubator/initiative
stage: seed | developing | drafting | refining | complete
created: YYYY-MM-DD
updated: YYYY-MM-DD

# Classification
domain: assessments | platform | cross-product
themes: []  # Categorization tags, same as ideas

# Initiative-Specific
organizing-question: null  # The central strategic question this initiative answers
strategic-narrative: null  # 2-3 sentences on why these ideas cluster together
child-ideas: []  # Authoritative list of child idea filenames (without path or .md)

# Tracking
source: inbox | slack | conversation | meeting
output-file: null  # Path to initiative-level output document, if one is produced
research: []
blocked_by: null
---
```

**What initiatives do NOT have:** Impact dimensions (`customer-sentiment`, `user-experience`, etc.). Those belong on child ideas. An initiative's strategic value is emergent from its children.

## Child-to-Parent Reference

Child ideas reference their parent via the `Initiative` relation (the `initiative` front-matter key):

```yaml
initiative: authentic-assessment-bts27  # Initiative filename without .md
```

The initiative card maintains the authoritative `child-ideas:` list. One parent per idea.

## Initiative Stage Model

Initiatives follow the same stage names but with different semantics:

| Stage | Meaning for Initiatives |
| ------- | ------------------------ |
| **Seed** | Framing exists — organizing question, narrative, children identified. Children may still be seeds. |
| **Developing** | Children actively developing. Initiative narrative enriched as research reveals patterns across children. |
| **Drafting** | Decision made: does this initiative produce its own synthesis output doc? If yes, drafting begins. |
| **Refining** | Initiative output doc being refined. |
| **Complete** | Initiative output finalized, or children have shipped individual outputs and the initiative served its organizing purpose. |

## Output Format Heuristic

Initiatives are probable candidates for **strategy docs** — they frame a strategic argument across multiple proposals. Child ideas are probable candidates for **product briefs** — they're discrete, scoped proposals with specific deliverables. This isn't a hard rule (a child idea with broad strategic implications might warrant a strategy doc), but it's the default expectation when choosing output format at the Stage 2→3 gate.

## Initiative File Naming

Same convention as ideas for the Slug: kebab-case, no special suffix. Distinguished by the `Type` field (`initiative`).

## Initiative Body Template

```markdown
## [Initiative Title]

**Organizing question:** [The central strategic question]
**Strategic narrative:** [2-3 sentences — why these ideas compose into something larger than any single one]

### Child Ideas
- [child-idea-1] — [one-line summary of its role in the initiative]
- [child-idea-2] — [one-line summary]
- ...

### Original Capture
[Verbatim original capture if the initiative originated from inbox]
```
