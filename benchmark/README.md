# Benchmark vault

`vault-template` is the clean copy of the vault used by the 20 benchmark tests. Agents never work in it.
They work in a live copy, which `reset-vault.ps1` builds outside the repo at `%USERPROFILE%\obsidian-bench\vault3`,
so agents under test can't wander into the repo and read the plugin's files. Open that folder in Obsidian, not
`benchmark` or `vault-template`.

```powershell
powershell -ExecutionPolicy Bypass -File benchmark\reset-vault.ps1
```

Run the script before every test. It only rewrites files that differ, and it refuses to touch a folder
that isn't marked as a benchmark vault.

## Expected answers

These are kept outside the repo, with the test plan, so agents under test can't read them.

## Set up by hand

B4-B5 use File Recovery history, which lives in the app and can't come from the template. Edit `Recovery Test`
so File Recovery saves earlier versions. Each reset of this note adds a version, so read the expected count from
`history` before each run. For B5, also check with `history:read` that the newest saved version differs from the
current note, otherwise a restore can't be told apart from doing nothing.

## Sync tests

B1-B3 run read-only on the real synced vault, not on this one. No test setup or edits are made for them.

## Reset limits

- Settings and theme changes (B9, B10) need an Obsidian restart after a reset.
- Reset can't remove Sync or File Recovery history.
