# Obsidian CLI - WorkSwarm Plugin

**Obsidian CLI for WorkSwarm**: a WorkSwarm plugin that lets the agent work with your Obsidian vault through
Obsidian's official CLI. Besides reading and editing notes, it reaches things file edits can't, such as Sync status
and history, File Recovery, Bases, commands, plugins and themes.

Windows only. For what the plugin does, what it needs and its safety notes, see the
[plugin README](plugin/obsidian-cli/README.md).

This is an independent project. It isn't made or endorsed by Obsidian.

## Install

1. Get `obsidian-cli-<version>.zip`, either from WorkSwarm's Hub or by building it (below).
2. Import the zip as a local plugin in WorkSwarm, then attach it to a chat.
3. In Obsidian 1.12.7 or later, turn on the CLI under Settings > General, and keep Obsidian running with your
   vault open.

## Repo layout

| Path | What it is |
| --- | --- |
| `plugin/obsidian-cli/` | The plugin: manifest, README, icon, skill (`skills/obsidian-cli/`) and tool (`tools/obsidian_cli_tool.py`) |
| `plugin/package.ps1` | Builds `plugin/dist/obsidian-cli-<version>.zip` from the plugin folder |
| `plugin/tests/` | Unit tests (`test_tool.py`) and tests against a running Obsidian (`test_live.py`) |
| `benchmark/` | The test vault template and the script that resets the live test vault |

## Build

```powershell
powershell -ExecutionPolicy Bypass -File plugin\package.ps1
```

The version in the zip's name comes from `manifest.json`. For a new release, bump the version in the manifest
(including the "Version x.y.z" in its descriptions) and add an entry to the plugin README's Updates section.

## Tests

```powershell
pip install pytest
python -m pytest plugin\tests
```

The unit tests don't need Obsidian or WorkSwarm; `conftest.py` stands in for openjiuwen when it isn't installed.
The live tests are skipped unless `OBSIDIAN_LIVE=1` is set. They need Obsidian running with the benchmark vault
open and registered as `vault3`, and they reset that vault as they run.

## Benchmark

`benchmark/vault-template` is a clean vault for 20 tests: 10 everyday tasks (search, tasks, properties, daily notes,
links, rename) and 10 that need Obsidian itself (Sync, File Recovery, commands, Bases, plugins, themes).
`benchmark/reset-vault.ps1` copies it to `%USERPROFILE%\obsidian-bench\vault3`, outside the repo, so agents under
test can't read the plugin's files. See [benchmark/README.md](benchmark/README.md).

Results for 0.1.1, one run per test, scored 1 (correct), 0.75 (correct after retries), 0.5 (partly correct) or 0:

| Agent | Everyday tasks | Needs Obsidian | Total |
| --- | --- | --- | --- |
| WorkSwarm | 6.5 / 10 | 2 / 10 | 8.5 / 20 |
| WorkSwarm + Obsidian CLI 0.1.1 | 7.25 / 10 | 7.75 / 10 | 15 / 20 |

## Versions

Each release is tagged (`v0.1.0`, `v0.1.1`). Changes are listed in the plugin README's Updates section.
