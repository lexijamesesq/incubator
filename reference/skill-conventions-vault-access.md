# Skill Conventions: Vault Access

> One section of the `incubator-reference.md` reference index — see it for the full section map.

**Rule:** Skills and agents read and edit vault files with the native tools (`Read`, `Grep`, `Glob`, `Edit`, `Write`). Declare the ones the skill uses in `allowed-tools` (skills) or `tools` (agents). Vault-relative paths resolve against the vault root.

| Operation | Tool |
| --- | --- |
| Read a note or its frontmatter | `Read` |
| Read several notes | parallel `Read` calls |
| Search content / frontmatter | `Grep` |
| List directory contents | `Glob` |
| Targeted string replace, frontmatter update, tag change | `Edit` |
| Create / overwrite | `Write` |
| Move / rename | Obsidian CLI via `Bash` (`obsidian move path="..." to="..."`) — wikilink-safe; a plain `mv` leaves links dangling |
| Delete | Only with explicit human confirmation, via `Bash` `rm` |

**Verification:** When updating a skill's `allowed-tools`, also update the agent's `tools` field if the skill has an associated agent definition. The two should match for vault operations. The `develop-synthesis` agent definition is the canonical reference example.
