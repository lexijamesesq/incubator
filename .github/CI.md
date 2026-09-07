# CI workflow shape

This repo follows dotty's CI shape (`.github/CI.md` there — least-privilege
`permissions:`, `concurrency:` with `cancel-in-progress`, `timeout-minutes`
on every job, SHA-pinned actions) and wiki's release-gate shape
(`.github/CI.md` there — `release-check`/`release-tag` split, the
`<plugin>--v<semver>` tag convention, `core-skills`'s shared, generic
release scripts). This file records the decisions specific to this repo,
not a duplicate of either.

## Decisions recorded here so they aren't re-proposed without new facts

**`check-plugin-version.sh`/`tag-plugin-release.sh` are called with
`plugins/incubator`, not `.`, as `plugin_dir` — copy this argument
carefully if you're copying this shape into a fourth repo.** Every other
repo publishing a plugin this way (`wiki`, `core-skills`, `dotty-private`)
keeps the plugin manifest at its own repo root, so `.` is the correct
`plugin_dir` there. This repo's plugin content lives at
`plugins/incubator/` (moved there from `.claude/{skills,agents}`
at the repo root). The first version of this repo's release-gate PR copied
wiki's workflow files verbatim, including the `.` argument — `release-check`
passed anyway on that PR because `check-plugin-version.sh` short-circuits
before ever reading `plugin.json` when no tag exists yet (the day-one case),
so the bug was invisible until `release-tag` actually tried to read the file
after merge and failed for real (`FileNotFoundError`). If this repo ever
gains a second plugin directory, or an existing one moves, this argument is
the first thing to check — not the shared scripts, which are already
generic and need no repo-specific edits.
