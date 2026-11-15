# Skill Conventions: Notion Access

> One section of the `incubator-reference.md` reference index — see it for the full section map.

Ideas, research artifacts, output documents and instance configuration live in Notion. This file is the one place the shared mechanics are stated: pointers, the calls, addressing an idea, artifact rows, writing to a card, how Notion returns text, configuration and persona. Every pipeline skill and agent follows it; a skill states only what is its own (its pointers, its arguments, the rows it touches, its steps) and points here for the rest. A sentence that would be true of more than one skill belongs here, not in a skill. `/competitive-landscape` works only against the research database and touches none of this.

## Pointers

The instruction file of the project the session runs in (`CLAUDE.md`, front matter) names where things are. If the front matter is not already in context, Read `CLAUDE.md`.

| Pointer | What it is |
| --- | --- |
| `notion_ideas` | URL of the Ideas database. One row per idea: the card is the row's page body, the front matter is the row's fields. |
| `notion_research` | URL of the Research database. One row per research artifact, related to its idea. |
| `notion_outputs` | URL of the Outputs database. One row per output document. |
| `notion_config` | URL of the Configuration page. Instance values, read by key name from its `yaml` block. |

The three database pointers are database URLs, never `collection://` data-source URLs: a database lists its view and its data source in one fetch, a data source lists no views.

**Overrides.** Every skill accepts the pointers it uses (`notion_ideas=`, `notion_research=`, `notion_outputs=`, `notion_config=`) as `key=value` arguments. An override replaces the pointer for that run. This is how a test run is kept away from the live rows: it passes scratch databases with the same fields. A run with overrides reads and writes only what the overrides name, and a skill that calls another skill or launches an agent passes every pointer in effect down with it, together with any `persona_file=` it was given.

**No pointers.** A skill that needs a pointer and finds neither an override nor a front-matter value stops and says which pointer is missing: `{skill} needs the {pointer} pointer (CLAUDE.md front matter, or a {pointer}= argument).` The shared lens skills run in other projects too: their `--adhoc` mode needs no pointer and makes no Notion call.

## Calls

Use only these connector tools (`mcp__notion__*`):

| Operation | Call |
| --- | --- |
| Read a row, a page or a database | `notion-fetch`. One fetch of a row returns its fields and its body. |
| Read the rows of a database | `notion-query-data-sources` in **view mode**. Never SQL or rows mode. |
| Create a row | `notion-create-pages` with a data-source parent: fields and a Markdown body in one call. |
| Set fields, including relations | `notion-update-page`, command `update_properties`. |
| Change part of a body | `notion-update-page`, command `update_content`, with a small `old_str` / `new_str` taken from a fresh fetch. |
| Append to the end of a body | `notion-update-page`, command `insert_content`. |
| Move rows to the trash | `notion-delete-pages` (in full, `mcp__notion__notion-delete-pages`). `/revert-to-seed` only, after the human has confirmed the exact list. See The trash, below. |

Never `replace_content` on an idea row: it would resend the Original Capture.

**Reading a database.** Fetch the database URL. The result lists its views as `view://...` URLs and its data source as a `collection://...` URL. Query the first view it lists, in view mode, passing the view URL as `view_url`, with `page_size` 100, passing `next_cursor` as `start_cursor` while `has_more` is true. Rows come back with their fields and their `url`, and no bodies. Keep the `collection://` URL: it is the parent for any row created in that database.

**Comparing row URLs.** A relation field holds row URLs. Two URLs name the same row when their 32-character ids match; ignore everything else in the URL.

**Empty fields.** A row's fetch leaves out a field or relation that has no value. A missing key means empty, not unknown.

**The trash.** `mcp__notion__notion-delete-pages` is the Notion connector's tool for moving pages to Notion's Trash; a database row is a page. It takes `page_ids` (1 to 20 per call, so a longer list takes several calls) and `user_confirmed`. Without `user_confirmed: true` it trashes nothing and returns the list of what it would trash; set it only after the human has confirmed that exact list. A trashed row leaves every view and is no longer returned by a query. Notion keeps it in the Trash for 30 days, during which it can be restored from the Trash in Notion or with the connector's `notion-restore-pages`; after that it is deleted for good. Trashing a row does not take it out of a relation that names it: the skill empties the relation itself (Fields, below). `/revert-to-seed` is the only skill that trashes anything, and only an idea's own Research rows; no skill trashes an idea row.

## Addressing an idea

- **Invoked by a person**, a skill takes an idea name and resolves it once against the Ideas view: exact match on Slug (after stripping a trailing `.md`), then a case-insensitive substring match on Slug or Name. Exactly one match: use it. Several: list them and ask. None: say so and list the slugs.
- **Invoked by another skill**, a skill is passed the idea row's URL in place of the name, and any artifact it must read as a row URL. It fetches the row and does not read the Ideas view, unless one of its own steps needs the whole portfolio (`/refine-seed`'s portfolio index does). The fetch names the database the row is in; if that is not the `notion_ideas` database in effect, it reports that and stops.
- An orchestrator resolves once and passes URLs down. Reading the whole Ideas view costs one page of rows per run; do it once.
- **An archived idea is out of the pipeline.** A row whose Stage is `archived` (a seed merged into another by `/refine-seed`, or an idea shelved at `/thesis-test`'s human gate) is skipped wherever a skill reads the Ideas view: resolving a name, listing ideas for the person to choose from, building a portfolio index or a theme vocabulary, matching related ideas. "Every row", "all rows" and "all ideas" in a skill mean the rows that are not archived. A skill handed an archived row's URL reports `Idea '{slug}' is archived.` and stops; a name that matches only an archived row gets the same message in place of "not found". Nothing un-archives a row but a person changing its Stage in Notion.

The idea's **slug** is the row's Slug field. It never changes; it is how reports and skills name the idea to a person.

## The idea row

What was front matter is a field of the row. What was the file body is the row's page body.

| Front matter | Field |
| --- | --- |
| `stage` | `Stage`: `seed`, `developing`, `drafting`, `refining`, `complete`, or `archived` (out of the pipeline; see Addressing an idea) |
| `domain` | `Domain` |
| `themes` | `Themes` (multi-select) |
| `created`, `updated` | `Created`, `Updated` (dates) |
| `related-ideas` | `Related ideas` (relation to Ideas rows) |
| `research` | `Research` (relation to Research rows) |
| `customer-sentiment`, `user-experience`, `revenue-potential`, `industry-disruption`, `strategic-alignment` | `Customer sentiment`, `User experience`, `Revenue potential`, `Industry disruption`, `Strategic alignment` |
| `output-format` | `Output format` |
| `output-file` | `Outputs` (relation to Outputs rows) |
| the file name | `Slug` |
| the `##` title | `Name`, and the `##` heading that opens the body |

The databases also carry fields left by the import of the old files that no skill reads or sets: `Output file` and `Unresolved references` on an idea row (`/revert-to-seed` clears `Output file`, nothing writes it), `File`, `Folder` and `Other front matter` on a Research row, `File` on an Outputs row.

**Fields.**

- A select or multi-select field takes only a value the field already has as an option. Never write a value outside a field's options. If the value you have is not an option, leave the field as it is and report it.
- A rating the evidence cannot support is left empty in the field. The card's table carries the words ("Insufficient data"). A skill that requires the five impact dimensions to be rated (`/draft`, `/jpd-push`) counts a dimension as rated when its field has a value, or when its field is empty and the card's Opportunity Assessment row for it says "Insufficient data" with a rationale. An empty field with no such row is unrated.
- A date is written as `date:{Field}:start` = `YYYY-MM-DD` with `date:{Field}:is_datetime` = 0. "Today" is the local date from `date +%Y-%m-%d`.
- A relation is written as a JSON array of row URLs. Writing a relation replaces the whole list, so send the full list.

## Research artifacts

A research artifact is a row in the Research database related to its idea. A skill finds an idea's artifacts through the idea row's `Research` relation and each row's `Research type`, never by a folder or a file name.

| Research type | Written by | Row Name |
| --- | --- | --- |
| `edtech-market-analysis` | `/edtech-sme` | `EdTech Market Analysis: {Idea Title}` |
| `tam-estimate` | `/tam-estimate` | `TAM Estimate: {Idea Title}` |
| `educator-sme-evaluation` | `/educator-sme` | `Educator SME Evaluation: {Idea Title}` |
| `divergent-angles` | `/divergent-thinking` | `Divergent Thinking: {Idea Title}` |
| `cross-domain-signals` | `/cross-domain` | `Cross-Domain Signals: {Idea Title}` |
| `synthesis-handoff` | `/develop` (`/thesis-test` appends to it) | `Research Handoff: {slug}` |
| `development-research` | `/develop` | `Development Research: {Idea Title}` |
| `thesis-brief` | `/thesis-test` | `thesis-brief ({slug})` |
| `thesis-test-partition` | `/thesis-test` | `thesis-test-partition-{date} ({slug})` |
| `thesis-test-lens` | a lens skill run under `/thesis-test` | `thesis-test-{lens}-{date} ({slug})` |
| `thesis-test-synthesis` | `/thesis-test` | `thesis-test-{date} ({slug})` |
| `falsification-record` | `/thesis-test` | `falsification-record-{date} ({slug})` |

These twelve names are the whole list: the `Research type` field needs each as an option, and no skill writes any other.

**A lens run under `/thesis-test`.** `/edtech-sme`, `/educator-sme` and `/tam-estimate` normally write the type and Name in their own row of the table. When the caller's execution contract names another Research type and Name for the artifact row (`/thesis-test` does: `thesis-test-lens`), the lens creates its row with those, and with the body the contract asks for. Everything else about creating the row is unchanged.

**Creating one.** One `notion-create-pages` call, with `allow_async` false so the row's URL comes back:

- **Parent:** the Research data source: fetch the `notion_research` database and take the `collection://` URL it lists. An orchestrator that has already fetched it passes that URL down as `research_data_source=`, and a skill given one uses it without fetching. (The fetch of an idea row cannot be relied on for this: the schema it shows is cut short.)
- **Fields:** `Name` (from the table above), `Idea` (a one-item array holding the idea row's URL), `Research type`, `Created` (today), and whatever else the skill's own step names.
- **Body:** the artifact from below its `#` title line. The title is the row's Name; the old front-matter block is the row's fields and is not repeated in the body.

If Notion refuses the create because a field lacks the option (a `Research type` not yet added, say), report which option is missing and put the artifact in the output so the work is not lost. Do not create the row under another value or without its type.

Setting `Idea` on the new row is what adds it to the idea's `Research` relation: the two are one relation seen from both sides. No separate write to the idea row is needed, and none is made.

**Never overwrite an artifact.** A run that produces an artifact creates a new row with today's date in `Created`, whether or not a row of that type already exists for the idea. Earlier rows stay. The exceptions are a row the same run created earlier and is still building (the `/develop` research trail), and the handoff row, which `/develop` and `/thesis-test` append to and correct in place.

**Finding them.** Fetch the idea row; its `Research` relation lists the artifact rows. Read the Research view and keep the rows whose `url` is in that list: each carries its `Research type` and `Created`. Then:

- "Does this idea have an artifact of type T" is "is there a kept row whose Research type is T".
- "The artifact of type T" is the kept row of that type with the latest `Created`. If two share the latest date, fetch both and take the one whose `page_last_edited_at` is later. If that does not separate them, list them and ask.
- To read every artifact of an idea whatever its type, skip the view and fetch each row in the relation.

Within one run, carry the row URLs that skills and agents return and fetch those; look rows up by type only when entering cold (a standalone run, or a resumed one).

## Output documents

An output document is a row in the Outputs database related to its idea: the document is the row's body, and the row's fields are `Name` (`{slug}-{output-format}`), `Idea`, `Format` (`strategy-doc` or `product-brief`), `Stage`, `Created` and `Updated`. `/draft` creates the row the way a Research row is created (one `notion-create-pages` call with `allow_async` false, the Outputs data source as parent, `Idea` a one-item array holding the idea row's URL), opening the body with the document's title as a bold line because Notion drops a leading `#` heading from a new row's body; setting `Idea` on it is what puts it in the idea row's `Outputs` relation, which stands where the `output-file` front-matter key did. `/refine` finds the document through that relation and edits its body the way a card is edited.

## Writing to a card

A card is the body of an idea row. Fetch the row first and work from the body as that fetch returned it; fetch again if anything has written to the row since.

- **Replace a block:** one `update_content` operation whose `old_str` is that one block's text exactly as fetched (a heading line, a paragraph, a list item, a table row).
- **Add a section in the middle:** `insert_content` only prepends or appends, so replace the heading the section goes in front of, as fetched, with the new section followed by that same heading. For example `old_str` `### Open Questions`, `new_str` `### Buildable Surface` + its list + a blank line + `### Open Questions`.
- **Remove a block:** an operation with that block as `old_str` and an empty `new_str`.
- **Skip what has not changed.** An operation whose `new_str` would equal its `old_str` is left out of the call.
- Write Markdown: a pipe table for a table, a blank line after each heading. Several lines that belong to one paragraph (a card's header fields) are written joined by `<br>` and nothing else; Notion returns them joined by `<br />`.
- An operation that matches nothing comes back as a warning when other operations in the call matched, and as a failed call when none did. Either way, fetch the row again and repeat that operation with text from the fresh fetch. `old_str` must be the text as Notion returns it (`<b>Core insight:</b>`, not `**Core insight:**`).

**Original Capture is never sent.** No `old_str` and no `new_str` contains the `### Original Capture` heading or anything below it: text that is never sent cannot be altered. "The `### Original Capture` heading" is the first heading in the body that begins that way; a merged seed carries a second, `### Original Capture (merged from: {slug})`, below it. The one write that adds text below the heading is `/refine-seed`'s merge, which appends the secondary's capture to the end of the primary with `insert_content`: an append sends only the new section, never the capture already there.

Write the body before the fields. A run that stops between the two leaves a card whose fields still say what stage it was in.

## How Notion returns text

A body does not come back byte for byte:

- `~`, `$` and `[ ]` come back escaped (`\~`, `\$`, `\[ \]`).
- A line break inside a paragraph comes back as `<br />`.
- Bold comes back as `<b>…</b>`, inline code as `<code>…</code>`.
- A blank line is added after each heading.
- A value that looks like a file name can come back wrapped as a link.

The words are preserved. Wherever a skill matches or compares text (a label such as `**Core insight:**`, a section heading, a field value, a surviving question, a quoted line), it compares normalised words: markup and escapes stripped, whitespace collapsed, case ignored. It never compares the raw strings.

Wherever a skill sends fetched text somewhere other than back to Notion (a Jira description, a file, a document in another store), it converts it back to Markdown first: `<b>` to `**`, `<code>` to backticks, `<br />` to a line break, escapes removed, a link added around a file name unwrapped.

## Configuration

Instance values are on the `notion_config` page, in `yaml` blocks: one block is the rule, but a page may hold more than one, and a key is read from whichever block holds it. Fetch the page and read a value by its key name (`role`, `persona_skill`, `example_card`, `approach`, `template_strategy_doc`, `template_product_brief`, `template_review`, `strategic_context.*`, `metrics.*`, `incubator.*`, `jira.*`, `cross_domain.*`). A key whose value is a Notion page URL names a page: fetch that page to read it. `.claude/instance.sample.md` is the public blank of the same keys.

**Local documents.** The strategy, OKR and NPS documents are local files, at the `path` each key gives. Skills read them with `Grep` and `Read`, never whole. An absolute path is used as it is; a relative path resolves against `workspace_root` from the user's global Claude Code configuration. Their `external_url` is what a citation links to; a local path never appears in a citation.

## Persona

The persona guide is the skill named by `persona_skill` on the Configuration page. Load it with the `Skill` tool.

A `persona_file=<path>` argument overrides it for a test run: Read that file in place of loading the skill. A path is absolute, or relative to the directory the session runs in. If the file's content is only a pointer elsewhere (a redirect note, a link, a "superseded by" line, with no voice guidance of its own), refuse it: report `Persona file {path} only points elsewhere. Pass the file that holds the guide, or leave persona_file= out to load {persona_skill}.` and stop. Do not follow the pointer, and do not go on without a persona.

## Tool lists

A skill declares the tools it uses in `allowed-tools`; its agent definition, where it has one, declares the same storage tools in `tools`. When one changes, change the other.

| The skill… | Declares |
| --- | --- |
| fetches a row, a page or a database | `mcp__notion__notion-fetch` |
| resolves an idea by name, or finds artifacts by type | `mcp__notion__notion-query-data-sources` |
| creates an artifact row or an output document's row | `mcp__notion__notion-create-pages` |
| writes a card body or sets fields | `mcp__notion__notion-update-page` |
| loads the persona | `Skill` |
| reads `CLAUDE.md`, a `persona_file=`, or a local strategy, OKR or NPS document | `Read` (and `Grep`, `Glob` for the local documents) |
| needs today's date | `Bash(date:*)` |

`Edit`, `Write` and `Bash(mkdir:*)` are not needed to reach ideas or research and do not belong in a skill's list. The one skill that keeps them is `/thesis-test`, for the local files its subject-mode writes.

`mcp__notion__notion-delete-pages` (The trash, under Calls) is deliberately in no list. `/revert-to-seed` is the only skill that calls it, and leaving it out of `allowed-tools` means the skill never pre-approves it: the session's own permission settings decide whether the harness asks before each call, on top of the confirmation the skill itself collects.
