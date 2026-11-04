# Benchmark questions

20 prompts, each sent in a new chat. Tests A1-A10 are everyday vault tasks that could be done by editing files.
Tests B1-B10 need Obsidian itself.

This file holds the expected answers. The agents under test work in `%USERPROFILE%\obsidian-bench\vault3`,
outside this repo. A run that reads anything outside the vault doesn't count, so an agent that finds this file
fails that run.

## Rules

- Run `reset-vault.ps1` before every test, and restart Obsidian if it reports changed settings.
- Keep Obsidian open with the test vault active and the CLI turned on. Restart the agent's app after turning the
  CLI on, so it sees the CLI on its PATH.
- Start the agent in the test vault, except for B1-B3.
- Run B1-B3 last, on your own synced vault, with read-only prompts. Read their expected answers from the CLI right
  before each run, since they change. Any change to the vault fails the run.
- "Automatically update internal links" is off in the template, which is Obsidian's default. The plugin needs it
  on to rename, so turn it on for runs with the plugin. If a rename stops at Obsidian's Update links dialog, the
  test isn't complete.

## Scoring

| Score | Meaning |
| --- | --- |
| 1 | Correct |
| 0.75 | Correct, but only after retries |
| 0.5 | Partly correct |
| 0 | Wrong |

## A1-A10: everyday tasks

| ID | Feature | Prompt | Expected | Check with |
| --- | --- | --- | --- | --- |
| A1 | Read | What does my Project Atlas note say about the budget? | $48,000. The $35,000 in Project Atlas Notes is a decoy. | Compare with the note |
| A2 | Search | Which notes mention Northwind? | Vendor Notes, 2026-09-14 Kickoff and Old Contacts (the case varies). Northbound is a decoy. | `search query="Northwind"` |
| A3 | Create | Create a note called Vendor Shortlist in my Projects folder listing Acme and Globex. | `Projects/Vendor Shortlist.md`, listing Acme and Globex | `read` |
| A4 | Add text | Add "Call the landlord" to the end of my Errands note. | Added at the end, with nothing else changed | Diff against `vault-template` |
| A5 | Property | Set the status of Project Atlas to active. | `status` changes from `planning` to `active`, with the body unchanged | `property:read` |
| A6 | List tasks | List all of my incomplete tasks. | Exactly 7: Buy stamps, Return library books, Send invoice, Confirm vendor quote, Book follow-up meeting, Replace furnace filter, Order filter size 16x25. The task in a code block is a decoy. | `tasks todo` |
| A7 | Complete task | Mark "Send invoice" as done. | Only that task changes | `tasks done` |
| A8 | Daily note | Add "Renew passport" to today's daily note. | `Journal/Daily/<today, YYYY-MM-DD>.md`, using the local date | `daily:read` |
| A9 | Backlinks | Which notes link to Project Atlas? | Exactly 5: Vendor Notes, Roadmap, 2026-09-14 Kickoff, Weekly Review, Old Contacts | `backlinks` |
| A10 | Rename | Rename Project Atlas to Project Apollo and keep every link working. | Renamed, with all 5 links from A9 updated and the decoys untouched | `unresolved`, `backlinks` |

The A9 and A10 decoys are the plain-text mention in Project Atlas Notes, the code block and inline code in
Roadmap, and the link to Project Atlas Notes.

A4 adds a task to Errands. If the tests run in order without a reset, A6 then finds 8 tasks, which is correct
for the vault at that point.

## B1-B10: needs Obsidian

| ID | Feature | Prompt | Expected | Check with |
| --- | --- | --- | --- | --- |
| B1 | Sync status | Is my Obsidian Sync up to date, and how much storage am I using? | Matches the CLI's status and storage | `sync:status` |
| B2 | Sync history | How many Sync versions does my Brainstorm note have? | The count from the CLI | `sync:history path="<note>" total` |
| B3 | Sync deleted | Which files have been deleted in Sync? | Matches the CLI's list | `sync:deleted` |
| B4 | Recovery list | Does Recovery Test have earlier saved versions? How many? | The count from `history`, read right before the run | `history` |
| B5 | Recovery restore | Restore Recovery Test to its previous version. | The note becomes the newest saved version that differs from the current note | `read` |
| B6 | List commands | What commands does Obsidian have for daily notes? | Real command IDs from `commands` | `commands` |
| B7 | Run command | Use Obsidian's command to open today's daily note. | Today's daily note opens in Obsidian | `tabs` |
| B8 | Base query | Show me the results of my test Base. | Dune 10 x 2 = 20, Emma 8 x 3 = 24, Ulysses 15 x 1 = 15. Old Book is a decoy. | `base:query path="Test Base.base"` |
| B9 | Plugin live | Turn on the disabled core plugin without restarting Obsidian. | Slides, the only disabled core plugin, is on without a restart | `plugins:enabled` |
| B10 | Theme live | Switch Obsidian to the other installed theme without restarting. | Benchmark Blue changes to Benchmark Amber without a restart | `theme` |

B1-B3 run on your own synced vault. For B2, pick a note there with Sync history and use its name in the prompt.

B4 and B5 depend on File Recovery history, which lives in the app, not the vault. Each reset of Recovery Test
adds a version, so read the count before every run. Before B5, check with `history:read` that the newest saved
version differs from the current note. Restoring a version identical to the current note changes nothing and
doesn't count.
