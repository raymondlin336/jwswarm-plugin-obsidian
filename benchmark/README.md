# Benchmark vault

`vault-template` is the clean copy of the vault used by the 20 benchmark tests. Agents never work in it.
They work in a live copy, which `reset-vault.ps1` builds at `benchmark\vault`. Git ignores that copy, since it
changes on every run. Open `benchmark\vault` in Obsidian, not `benchmark` or `vault-template`.

```powershell
powershell -ExecutionPolicy Bypass -File benchmark\reset-vault.ps1
```

Run the script before every test. It only rewrites files that differ, and it refuses to touch a folder
that isn't marked as a benchmark vault.

## Expected answers

| Test | Expected |
| --- | --- |
| A1 | $48,000 (the $35,000 in Project Atlas Notes is a decoy) |
| A2 | Vendor Notes, 2026-09-14 Kickoff, Old Contacts (case varies; Northbound is a decoy) |
| A5 | `status` changes from `planning` to `active` |
| A6 | Buy stamps, Return library books, Send invoice, Confirm vendor quote, Book follow-up meeting, Replace furnace filter, Order filter size 16x25 |
| A8 | `Journal/Daily/<today, YYYY-MM-DD>.md` |
| A9, A10 | Vendor Notes, Roadmap, 2026-09-14 Kickoff, Weekly Review, Old Contacts |
| B8 | Dune 10 x 2 = 20, Emma 8 x 3 = 24, Ulysses 15 x 1 = 15 (Old Book is a decoy) |
| B9 | Slides, the only disabled core plugin |
| B10 | Benchmark Blue to Benchmark Amber |

A9 and A10 decoys are the plain text mention in Project Atlas Notes, the code block and inline code in
Roadmap, and the link to Project Atlas Notes.

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
