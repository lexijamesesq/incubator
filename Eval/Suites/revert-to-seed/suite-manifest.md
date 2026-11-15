# Eval Suite: revert-to-seed

**Purpose:** A check a person can repeat that `/revert-to-seed` moves an idea's own research rows to Notion's Trash with the connector tool it names, empties the idea's Research relation, and leaves Original Capture as it was. The tool belongs to the Notion connector, not to this repository, so nothing in the repository can show that it exists. This check is the evidence.

**Created:** 2026-11-14
**Source:** Step 2 of `.claude/skills/revert-to-seed/SKILL.md`, and The trash in `reference/skill-conventions-notion-access.md`.

**Execution pattern:** Manual — matches `enrichment-skills/`. A person stages the rows, runs the skill, and fetches the rows afterwards.

**Fixture world:** The card comes from the `develop-synthesis` suite's fixtures, which are fiction set in one invented education market. Any developed card with an Original Capture section will do.

---

## Test case

### Trash two own research rows

**Setup:** an idea at Stage `developing` with exactly two Research rows, each related to that idea and to no other.

**Invoke:** `/revert-to-seed {slug}` with the scratch pointer overrides.

**Expected:**

- Before the person confirms, the skill lists the two rows (Name, Research type, URL) and trashes nothing.
- After the person confirms that list, the skill calls `mcp__notion__notion-delete-pages` once, with `page_ids` holding the two rows' IDs and `user_confirmed` true.
- The call returns each row's id, URL and title, and a note that the items are in Trash and can be restored.
- A fetch of each research row returns it marked `deleted`.
- A fetch of the idea row shows no `Research` relation (a fetch leaves out an empty relation), Stage `seed`, and the text under `### Original Capture` the same as before the run, word for word.

**Fail signals:** a trash call before the confirmation; a call to any other tool to remove the rows; a research row that fetches without `deleted`; a URL left in the idea's `Research` relation; any change under `### Original Capture`.

---

## How to run

1. **Stage the idea.** Load `Eval/Suites/develop-synthesis/Fixtures/Expected/absence-catch-up-pack.md` as a row in the scratch Ideas database, the way that suite's manifest describes (Loading a fixture), with a Slug of its own and Stage `developing`. To see the field reset as well, set `Output format`, `Blocked by` and the five ratings.
2. **Stage two research rows.** Create two rows in the scratch Research database, each with a `Research type` the field has as an option, a short invented body, and `Idea` set to the staged idea row only.
3. **Record the before state.** Fetch the idea row. Keep the two URLs in its `Research` relation and the text under `### Original Capture`.
4. **Run.** Invoke `/revert-to-seed {slug} notion_ideas=... notion_research=... notion_config=... persona_file=...`. The trash tool is in no skill's `allowed-tools`, so the session's own permission settings decide whether the call is prompted for. The recorded run below was a session that answers no permission prompts, with `mcp__notion__notion-delete-pages` allowed for that session.
5. **Confirm the list** when the skill asks. Check that no trash call was made before this point.
6. **Check the call.** In the session's tool calls, find `mcp__notion__notion-delete-pages` and its result.
7. **Fetch the two research rows.** Each should come back marked `deleted`.
8. **Fetch the idea row.** Check the `Research` relation, the Stage and the Original Capture against the before state.
9. **Finish the run.** The skill goes on to `/refine-seed`, which may stop to ask about related seeds in the scratch database. Answer as you see fit; nothing above depends on it.
10. **Teardown.** The two research rows are already in the Trash. Move the idea row there by hand.

---

## Recorded run

**2026-11-14**, in a headless session with the tool allowed for the session, on a staged idea with a `synthesis-handoff` row and an `edtech-market-analysis` row:

- The first turn listed both rows and stopped for confirmation. No trash call had been made.
- After confirmation the skill called `mcp__notion__notion-delete-pages` with the two page IDs and `user_confirmed: true`. The result listed both rows by id, URL and title, with the note `These items are in Trash. They can be restored with the restore_pages tool or from Trash in Notion.`
- Each research row then fetched with its page tag marked `deleted`. Its Name, Research type and Created were still returned; its body and its `Idea` relation were not.
- The idea row fetched with no `Research` relation, Stage `seed`, no ratings, no `Output format`, an empty `Blocked by`, and the Original Capture unchanged.

Not exercised: a row shared with another idea, a list of more than 20 rows, a declined confirmation, and restoring a row from the Trash.

---

## Version History

- **2026-11-14** — Suite created with one manual check and the run that produced it.
