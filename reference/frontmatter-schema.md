# Frontmatter Schema

> One section of the `incubator-reference.md` reference index — see it for the full section map.

In Notion each key below is a field of the idea's row in the Ideas database, and the file name is the row's Slug. `reference/skill-conventions-notion-access.md` maps key to field. Three keys are not plain fields: `research` is the row's `Research` relation (rows in the Research database), `output-file` is its `Outputs` relation (rows in the Outputs database), and `related-ideas` and `initiative` are relations to other Ideas rows. `null` below is an empty field; an impact dimension the evidence cannot support stays empty, with "Insufficient data" in the card's table. `research-ids` has no field and no skill writes it.

```yaml
---
type: incubator/idea
stage: seed | developing | drafting | refining | complete
created: YYYY-MM-DD
updated: YYYY-MM-DD
output-format: null | strategy-doc | product-brief

# Classification
domain: assessments | platform | cross-product
themes: []  # e.g., [authentic-assessment, marketplace, ai-capabilities]
# Theme governance:
# - Themes are provisional at Stage 1. /develop may add or remove at Stage 2 based on research.
# - Vocabulary is closed at /develop time — only use themes already in the portfolio.
#   New themes are created by the router at intake or by explicit human request.
# - ai-capabilities drives JPD "AI Feature" checkbox. /develop must explicitly assess
#   whether AI is load-bearing (see /develop Step 5d).
# - Minimum one theme per idea.

# Impact Dimensions (populated progressively, null until assessed)
customer-sentiment: null | none | low | medium | high
user-experience: null | none | low | medium | high
revenue-potential: null | none | low | medium | high
industry-disruption: null | none | low | medium | high
strategic-alignment: null | none | low | medium | high

# Relationships (human-set only — agents surface candidates, human confirms)
related-ideas: []  # idea filenames without path or extension, e.g., [ai-student-intelligence-model, ai-learning-pattern-recognition]
initiative: null  # parent initiative filename without .md, null if standalone

# Tracking
source: inbox | slack | conversation | meeting
output-file: null  # path to output document (populated at Stage 3)
research: []  # links to local research artifacts
research-ids: []  # UUIDs referencing research_findings rows in Snowflake (populated by /develop)
blocked_by: null  # terse reference — card title or theme blocking stage advancement

# JPD Integration (populated after push, null before)
jira-key: null  # e.g., PROJ-1234
jira-pushed-at: null  # YYYY-MM-DD
jira-sidecar-url: null  # Google Doc URL for the Research Sidecar; populated by /jpd-push on first push
---
```

**Impact dimension rationale:** Maps to Director/VP/C-Suite priorities. Customer sentiment → retention. User experience → engagement (MAU). Revenue potential → ARPU. Industry disruption → competitive positioning. Strategic alignment → organizational priority. Translates to MAU x ARPU = ARR.

**TAM / market sizing:** Not a frontmatter field. When market sizing data is relevant and available, include it in the Research Summary or Opportunity Assessment rationale in the body. Many ideas (platform capabilities, positioning plays) don't have a meaningful standalone TAM — forcing the field creates noise.

**Related ideas:** Human-set only. Agents surface relationship candidates during /develop Step 3; the human confirms which relationships are meaningful; the agent writes the confirmed relationships to frontmatter on all affected cards. The agent never autonomously populates this field.
