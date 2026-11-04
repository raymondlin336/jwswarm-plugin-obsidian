# Obsidian CLI (obsidian-cli)

**Version 0.1.1**

Lets WorkSwarm work with your Obsidian vault through Obsidian's official CLI, including features that aren't possible by editing files alone, such as Sync status, file history, Bases, plugins and themes.

## 中文

让 WorkSwarm 通过 Obsidian 官方命令行操作你的笔记库，包括仅靠编辑文件无法完成的功能，例如同步状态、文件历史、Bases、插件和主题。

## Requirements

- **Windows only.** Mac and Linux aren't supported.
- **Obsidian is running**, with your vault open.
- **The CLI is turned on**, under Settings > General > Advanced.
- **To rename or move notes**, turn on "Automatically update internal links" under Settings > Files and links. If it's off, the agent asks you to turn it on and leaves the note as it is.

If Obsidian is installed in a custom location, the agent asks you for the full path to `Obsidian.com`.

## Core capabilities

- **obsidian-cli (skill)**: Tells the agent when to use the CLI instead of editing vault files, which commands fit each job, and how to handle each kind of failure. It also tells the agent to ask before deleting or restoring.
- **obsidian_cli (tool)**: Runs any Obsidian CLI command and returns the result. It selects the vault reliably, stops commands that hang, reports open Obsidian dialogs, and returns CLI errors as failures.

## Additions beyond the CLI

The tool's `command`, `options`, `flags` and `vault` inputs map directly to the Obsidian CLI. The plugin adds:

- **`cli_path` (tool input):** The full path to `Obsidian.com`, used when Obsidian isn't in the default location. The agent asks the user for this path. The file must exist and be named `Obsidian.com`, and the path isn't saved between chats.
- **Link setting check:** Before a rename or move, the tool checks that links will update automatically. If they won't, it stops before changing anything.
- **Time limit:** A command stops after 30 seconds, and the tool reports any dialog open in Obsidian.
- **Vault selection:** The tool runs the CLI from outside any vault, so the agent's working folder can't select the wrong vault.
- **Backslash check:** The CLI saves a backslash followed by `n` or `t` as a line break or tab, with no way to escape it. The tool refuses text containing either, so a note is never saved wrong, and the agent writes that text with its own file tools instead.

## Permissions and safety

- **Full CLI access:** The tool passes every CLI command through, including commands that run code inside Obsidian (`eval`, `dev:*`) and install community plugins and themes. Nothing is blocked, so only use it with vaults and content you trust.
- **Approvals:** The skill tells the agent to ask before it deletes files, restores an earlier version, pauses Sync or restores a Sync version, runs code with `eval` or `dev:*`, or installs, uninstalls or disables plugins and themes. This is guidance, not enforcement. To approve the tool's calls yourself, set `obsidian_cli` to `ask` in WorkSwarm's tool permissions.
- **Dependencies:** Python standard library only. The tool does nothing at import time and doesn't store any settings.

## Not affiliated with Obsidian

This is an independent plugin. It isn't made or endorsed by Obsidian.

## Updates

### 0.1.1

- The skill now says that Sync status only describes this device, so the agent shouldn't claim other devices are in sync.
- The listing description now says Obsidian must be running with its CLI turned on.
- The safety section now lists every action the skill asks about first.
- The tool refuses text containing a backslash before `n` or `t`, which the CLI would garble, and the agent writes it with its own file tools instead.

### 0.1.0

- Initial version: one tool and one skill for working with Obsidian through its CLI.
