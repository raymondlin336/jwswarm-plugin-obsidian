# Obsidian CLI command guide

Common commands for the `obsidian_cli` tool. For anything else, use `help`, which lists every command and option.

In the tables, `key=value` goes in `options`, and a bare word goes in `flags`.

Most commands that act on a file accept either of these:

- `file=<name>` finds a note by name, like a wikilink. Example: `file=Project Atlas`.
- `path=<path>` is the exact path from the vault root. Example: `path=Projects/Project Atlas.md`.

Use `path` when two notes could share a name.

## Notes

| Request | Command | Inputs |
| --- | --- | --- |
| Read a note | `read` | `file` or `path` |
| Create a note | `create` | `path`, `content` |
| Add to the end of a note | `append` | `file` or `path`, `content` |
| Add to the start of a note | `prepend` | `file` or `path`, `content` |
| Show headings | `outline` | `file` or `path` |
| Delete a note (ask first) | `delete` | `file` or `path` |
| Rename a note | `rename` | `file` or `path`, `name` |
| Move a note | `move` | `file` or `path`, `to` |

## Finding things

| Request | Command | Inputs |
| --- | --- | --- |
| Which notes mention some text | `search` | `query`, optional `path`, `limit`, flag `case` |
| Show the matching lines | `search:context` | `query`, optional `path`, `limit` |
| List files | `files` | optional `folder`, `ext`, flag `total` |
| List folders | `folders` | optional `folder`, flag `total` |
| Recently opened files | `recents` | flag `total` |
| List tags | `tags` | optional `file`, flags `counts`, `total` |

`search` ignores case by default. Prefer it over searching vault files yourself.

## Links

| Request | Command | Inputs |
| --- | --- | --- |
| Which notes link to this note | `backlinks` | `file` or `path`, flags `counts`, `total` |
| What this note links to | `links` | `file` or `path`, flag `total` |
| Broken links | `unresolved` | flags `verbose`, `counts`, `total` |
| Notes nothing links to | `orphans` | flag `total` |
| Notes that link to nothing | `deadends` | flag `total` |

Use `backlinks` instead of searching for `[[Name]]`. It includes aliases, heading links, embeds and Markdown links, and it excludes examples in code blocks.

## Tasks

| Request | Command | Inputs |
| --- | --- | --- |
| Incomplete tasks | `tasks` | flag `todo`, optional `file` or `path`, flags `total`, `verbose` |
| Completed tasks | `tasks` | flag `done`, optional `file` or `path` |
| Mark a task done or not done | `task` | `path`, `line`, flag `done` or `todo` |

`tasks` skips examples in code blocks. To change a task:

1. Run `tasks` with flags `todo` and `verbose`, adding `file` if you know the note. The output groups tasks by file and gives each one's line number.
2. Run `task` with `path`, `line` and the flag `done`. You can also pass `ref=<path>:<line>` instead of `path` and `line`.
3. Check that the output shows the task you meant.

## Properties

| Request | Command | Inputs |
| --- | --- | --- |
| Show a note's properties | `properties` | `file` or `path` |
| Read one property | `property:read` | `name`, `file` or `path` |
| Set a property | `property:set` | `name`, `value`, `file` or `path`, optional `type` |
| Remove a property | `property:remove` | `name`, `file` or `path` |

Use these instead of editing the frontmatter by hand.

## Daily notes

| Request | Command | Inputs |
| --- | --- | --- |
| Where today's note goes | `daily:path` | none |
| Read today's note | `daily:read` | none |
| Add to today's note | `daily:append` | `content` |
| Add to the start of today's note | `daily:prepend` | `content` |
| Open today's note | `daily` | none |

Use these instead of guessing the date format or folder. They fail with `Folder "..." not found` if the daily notes folder doesn't exist. If that happens, tell the user or ask before creating the folder.

## Bases

| Request | Command | Inputs |
| --- | --- | --- |
| List Bases | `bases` | none |
| Show a Base's results | `base:query` | `path`, optional `view`, `format` |

Use `path` with the `.base` extension, such as `path=Test Base.base`. In testing, `file=Test Base` failed even though `help` lists it. The results include calculated formula columns. `format=tsv` or `format=md` is easier to read than the default JSON.

## Sync

| Request | Command | Inputs |
| --- | --- | --- |
| Status and storage | `sync:status` | none |
| A note's Sync versions | `sync:history` | `file` or `path`, flag `total` |
| Read a Sync version | `sync:read` | `file` or `path`, `version` |
| Restore a Sync version (ask first) | `sync:restore` | `file` or `path`, `version` |
| Files deleted in Sync | `sync:deleted` | flag `total` |
| Pause or resume Sync (ask first) | `sync` | flag `off` or `on` |

- `sync:status` returns `status`, `vault`, `vault size` and `account usage`, such as `18.39 MB / 1.00 GB`. Work out the storage left from `account usage`.
- Statuses seen so far are `synced`, `syncing` and `disconnected`, and there may be others. `disconnected` comes with a message that Sync isn't set up for this vault.
- If Sync isn't set up, `sync:history` and `sync:deleted` return an error.

## File history

These use File Recovery, which is local and separate from Sync.

| Request | Command | Inputs |
| --- | --- | --- |
| A note's saved versions | `history` | `file` or `path` |
| Read a saved version | `history:read` | `file` or `path`, `version` |
| Restore a saved version (ask first) | `history:restore` | `file` or `path`, `version` |
| Files that have history | `history:list` | none |

- Version 1 is the newest saved version, which may not match the note's current text.
- Before restoring, read the version with `history:read` and compare it with the current note.
- A restore can add a new saved version, so the numbers can shift afterward.
- `history:list` and `recents` can include files that have since been renamed or deleted.

## The app

| Request | Command | Inputs |
| --- | --- | --- |
| What's open | `tabs` or `workspace` | none |
| Open a note | `open` | `file` or `path`, flag `newtab` |
| List app commands | `commands` | optional `filter`, a prefix such as `daily-notes` |
| Run an app command | `command` | `id` |
| Current theme | `theme` | none |
| Installed themes | `themes` | none |
| Switch theme | `theme:set` | `name` |
| Installed plugins | `plugins` | `filter=core` or `filter=community` |
| Enabled plugins | `plugins:enabled` | `filter=core` or `filter=community` |
| Turn a plugin on (ask first if it's not what the user asked) | `plugin:enable` | `id`, `filter=core` or `filter=community` |
| Turn a plugin off (ask first) | `plugin:disable` | `id`, `filter=core` or `filter=community` |
| Vault details | `vault` | optional `info=name`, `path`, `files`, `folders` or `size` |
| Known vaults | `vaults` | flags `verbose`, `total` |

## Content formatting

The tool converts real line breaks and tabs in `options` values into the form the CLI expects, so you can pass normal multi-line text. A literal backslash followed by `n` will be read as a line break.
