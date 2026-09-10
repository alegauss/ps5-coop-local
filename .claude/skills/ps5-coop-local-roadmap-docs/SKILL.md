---
name: ps5-coop-local-roadmap-docs
description: How to work a task in this project's roadmap — the three docs/ files (ROADMAP.md, CHANGELOG.md, IMPROVEMENTS.md) owned by the roadkeep CLI and never hand-edited, and above all the one-task-one-commit rule: every finished roadmap task ends with `run-commit.cmd -m "<title>"` from the repo root, code plus doc sync in that single commit. Use whenever adding a task, picking the next CL-number, marking a task shipped, retiring, deferring, linting, editing any of those files, executing a block or a list of CL ids, or finishing any task that touches this repo.
---

# Roadmap tasks & committing

**No figure in this file is derived from the backlog.** Counts, the priority queue and
which ids are open are all things `roadkeep` answers, and a sentence here quoting one is a
sentence that was true on the day it was written. Where you would want a number, this file
names the read instead. Keep it that way.

## ⛔ READ FIRST — one task, one `run-commit.cmd` (non-negotiable)

**A task is not finished until the commit landed.** The commit tool is
`run-commit.cmd` (on the OS PATH, in `D:\Dev\bin`) — never `git commit` by hand:

```
cd d:\Git\alegauss\ps5-coop-local
run-commit.cmd -m "<conventional-commits title, ASCII>"
```

- **Always pass `-m`.** It stages everything and generates the body from the staged
  diff; without a title it infers one, and for a docs/ROADMAP commit that means prose
  about already-shipped work gets misread as `feat: implement <feature>`.
- **ASCII in the title.** An em dash or an accent goes through `cmd` and may not arrive
  as the bytes you typed.
- **`cd` to the repo root first** — `run-commit.cmd` stages relative to CWD.
- **The doc sync rides in the same commit as the code**, so the governed files never
  describe a state that did not ship.
- **You may NOT do more than one task before committing.** A multi-task request
  (a whole block, or a list of `CL<n>`s) is _not_ permission to batch: it is a request
  to run them one at a time, committing after each. One giant diff spanning many tasks
  is the failure this rule exists to prevent.
- **A batch of ≥2 tasks runs under the `/loop` skill** (self-paced): exactly one task
  per iteration, `run-commit.cmd` at the end of that iteration, then advance. Do not
  hand-roll a loop that defers commits to the end.
- **Self-check before starting task N+1:** `git status` / `git log -1`. If the previous
  task's work is still in the working tree, stop and commit it first.
- **Declare your paths, then read them back at the moment of committing.** A claim is dated
  by a marker write and released when the marker moves, for the window `[claims] held` sets.
  `roadkeep claim CL<n> --path <p>` says what the task will touch; **`roadkeep claim CL<n>`
  with no `--path` answers what you declared plus what the tree holds that another live claim
  says is its own — the analysis `git add -A` cannot make.** `roadkeep claims` lists held,
  expired and stale, and `[claims] held` in `roadkeep.toml` is how long one stands.

The same rule applies to any finished unit of work in this repo, roadmap task or not:
when the work is done and validated, commit it with `run-commit.cmd -m "…"` rather than
leaving it in the tree.

## The gate before the commit

Validated means the project's own gate was run, not that the edit looked right.

**`roadkeep lint` is the one gate that holds on every task, without exception** — it is the
only gate a docs-only change has, and non-zero exit is the whole point of it. `roadkeep
repair` spends a whole report in one call, and `roadkeep explain <code>` says what a finding
means before you guess.

Beyond that, **this repository declares no build and no test yet** — there is no
`package.json`, no compile step and no runner. Do not invent a `compile.cmd`, an `npm test`
or a `npm run typecheck` here because a sibling repo has them. The gates arrive with the
work that introduces them:

- **CL7** puts the first site in the tree. Whatever it declares — a dev server, a
  formatter, a linter — becomes a gate from that commit on, and belongs in this table.
- **CL21** is the dataset validator. Once it exists, every task that touches `data/` runs
  it, because a static site has no server to catch bad data at request time.

So until then: read the repo root for what it actually declares (`package.json`, a
`Makefile`, a `*.cmd`), run what is there, and where nothing is, say plainly in the commit
that the change was verified by reading and by `roadkeep lint`. A screenshot beats a claim
that a screen renders.

**Name EVERY task id an assertion holds, not just the one you are working.** A test written
under one id often ends up holding the task that finished the work, and naming both is four
characters, while the alternative is a second test file written to move a number.

## ⛔ READ SECOND — three files are owned by `roadkeep`

[`roadkeep.toml`](../../../roadkeep.toml) declares this project's format — prefix `CL`,
`ref_scheme = "id"`, the markers, the limits — and [`.mcp.json`](../../../.mcp.json) plus
[`.claude/settings.json`](../../settings.json) wire the rest through the launcher at
`../roadkeep/scripts/roadkeep.py`: a hook that **denies a hand-edit** to any governed file
and names the command that does it, the `mcp__roadkeep__*` tools whose input schema _is_
this project's format, and the upstream [`roadkeep`](../roadkeep/SKILL.md) skill with the
whole write path. **Reach for the MCP tools first**; the shell fallback is `roadkeep` on
PATH or that launcher.

Start a task with `brief`, not by reading the files; `lint` is the gate.

Each file has one job — never duplicate content between them:

| File                                                    | Single responsibility                                                                                                                                                                                             |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`docs/ROADMAP.md`](../../../docs/ROADMAP.md)           | **Task status** — active backlog only (📋 designed · 💭 idea · ⏳ partial · 🛠 in-progress), one line per task, plus the `## Priority` queue, the block headings, the `## Done when` criteria and the `## Non-goals`. |
| [`docs/CHANGELOG.md`](../../../docs/CHANGELOG.md)       | What has **shipped** — the ledger, indexed by block. Authoritative for the highest block letter.                                                                                                                  |
| [`docs/IMPROVEMENTS.md`](../../../docs/IMPROVEMENTS.md) | **Design rationale** for _unshipped_ work only. Deleted per task by the ship that closes it.                                                                                                                      |

**`[files]` in `roadkeep.toml` declares those three and no more** — this project has no
`DECISIONS.md` and no deferred store. A constraint that outlives the work therefore goes to
`criterion add` or `non-goal add`, which are never deleted; if you genuinely need a decision
record or a deferred store, declare the file first (`roadkeep declare`) rather than reaching
for a flag that has nowhere to write.

## The loop

- **`brief --claim`** picks the next line and briefs it in one read, taking it in the same
  transaction. **Reach for `--designed`** where you asked to execute and not to plan — an
  unscoped pick can hand you a `section add` and not a commit. `list --marker 💭` says how
  much of the backlog still has its design to write.
- **Order is the `## Priority` section of `docs/ROADMAP.md`**, not `roadkeep.toml` and not
  opinion. `priority list` is the read; an empty queue means the tier is off and `pick`
  falls through to the lowest ready id. `priority add` / `priority drop` are the doors.
- **The read BEFORE an add is `delivered <block> --near "<the sentence you would file>"`.**
  It ranks that block's nearest deliveries against what you are about to propose, which is
  the duplicate question asked _before_ an id is spent.
- **Adding is `add --block <x> --symptom "…" --why "…" --section "…"`.** The `§CL<n>`
  pointer is derived. A line whose section is missing is a `ref.unresolved` finding, so
  file both halves in the one transaction. `budget` prices every field first.
- **The next id is `roadkeep next-id`** — it scans every governed file and never fills a
  gap. Retired ids are never reused.
- **Keep a task line terse** — symptom (what does not work, never a fix name) + one
  sentence of why + the pointer. The reasoning belongs in the section.

## The two lists that bind a proposal

Both are governed here and both are checked _before_ work becomes a line:

- **`non-goal list`** — every entry binds. Online-only coop, prices and buy links, other
  platforms, and anything needing a backend are already filed there, and a proposal a
  non-goal forbids is not filed. Where one merely _bounds_ a line without forbidding it,
  the gate says so (`non-goal.reaches`) and the answer is recorded by quoting that lead in
  the line's own design section.
- **`criterion list`** — what would finish each block, under `## Done when — Block X`.
  **A constraint the project must keep obeying usually belongs here**: a criterion survives
  every ship, is never deleted, and is what `ship --checked <lead>` verifies.

## Shipping, and the section it deletes

`ship <id> --why "<what now works>"` writes the ledger entry, clears the roadmap line and
**deletes the design section**, in one transaction or none. That deletion is correct — a
design says how the work was built and stops being true when the code moves — but it is
the last moment anything in that section can be saved.

**Read the section before you ship it**, and ask of each paragraph: _does this stop being
true when the code moves?_ The doors, in order of how often they are the right one:

| Answer                                     | Door                                                                                                       |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| It explains **this module**                | `--recorded-in <path>` — move the prose into that file's docstring or header. **This is the common case.** |
| It is a rule the project must keep obeying | `criterion add` or `non-goal add`, which are never deleted — not a ship flag at all                        |
| You read it and it had gone stale          | `--superseded-design "<what it was wrong about>"`                                                          |
| Nothing survives                           | ship plainly — most ships are this                                                                         |

**Never copy a section into a second file.** That is the accreting rationale this format
exists to refuse.

**A design section may carry its own instruction.** Where the author already knew what
would survive, the section ends with a line naming it — `On ship: --recorded-in <path>`.
Honour it, revised against what was actually built.

## Everything else

- **Status lives in exactly one file.** If a marker anywhere disagrees with the roadmap, the
  roadmap wins.
- **A pause is `defer <id> --reason "…"`, not `retire`.** Retiring is terminal: the id cannot
  come back, the resolver reads the dep as never, and the section is deleted.
- **A false claim is `restate <id> --symptom "…"`**, which keeps the id, the deps, the marker
  and the design — not `retire` plus `add`, which spends an id and deletes a design that was
  right.
- **`lint` reports and `repair` spends the report** — every finding names the command that
  closes it, and `explain <code>` says what a code means before you guess.
