# PS5 local co-op

A catalogue of PlayStation 5 games you can play **on one console, in one room, with
the people who are actually there**. It is a static page: a grid of covers you can
search, filter by how many fit on the couch, and sort.

## The inclusion rule

**Local co-op on a single PS5.** Two or more people, one console, one television.

That rule is the whole point, and it is worth stating first because it settles the
argument this kind of list always attracts:

- **Online co-op does not count.** A game you play together over the network is not
  what this catalogue is for, however good it is. If it needs a second console or a
  second copy, it is out.
- **Split screen, shared screen and pass-the-controller all count.** They play
  nothing alike, so the catalogue records which one a game uses instead of flattening
  them together.
- **Co-op in one mode still counts**, and the game says so. Call of Duty: Black Ops
  Cold War is local only in Zombies; Mortal Kombat 11 only in the Towers of Time. That
  caveat is on the game's detail panel, because it is the fact that decides a purchase.

Also deliberately absent: prices and buy links, other platforms, and any kind of
account, rating or comment. There is no backend and there is not going to be one.

## Where the list came from

`data/source-list.txt` is the list as it was received, verbatim, one entry per line.
It is provenance and is never edited to "fix" an entry — corrections happen in the
worksheets that read it, so the original claim stays visible next to the correction.

Those 195 lines are not 195 products. Four repeat verbatim, three name one game under
two names, and about a dozen name a franchise or a bundle rather than something the
store sells — "King of Fighters" is a series, "Diablo III e IV" is two games at once,
and "Minigolf" is a listing nobody has been able to find. Resolving that leaves 180
entries: `data/canonical.csv` renames what has a real title, splits what names more
than one product, and drops what PS5 does not sell, each with its reason on the row.

Twelve of those 180 then fail the inclusion rule — Returnal, Fall Guys, Astroneer and
nine more are real PS5 games whose co-op needs a network — so `data/excluded.csv` keeps
them out and says why. That leaves **168 entries**.

## Running it

There is no build step and no framework. One line, from the repository root:

```sh
python3 -m http.server
```

Then open <http://localhost:8000>. Opening `index.html` directly will not work: the
page fetches `data/games.json`, and a browser blocks that over `file://`. The page
says so if you try.

## Regenerating the data

`data/games.json` is generated and committed, because a static site has no server to
build it on demand. After editing any worksheet:

```sh
python3 scripts/build_dataset.py     # worksheets -> data/games.json
python3 scripts/build_covers.py      # a fallback cover for every game
python3 scripts/validate_dataset.py  # refuse a broken catalogue
```

CI runs all three and refuses to publish if the committed output no longer matches
its sources.

Two more scripts fill worksheets, and are deliberately not part of that loop:

```sh
python3 scripts/fetch_covers.py --dry-run  # report what it would match
python3 scripts/fetch_covers.py            # download the packshots
python3 scripts/fetch_years.py --dry-run   # report the years it would write
python3 scripts/fetch_years.py             # fill data/catalog.csv's year column
```

Both go to the network, so CI cannot run them and a build must never depend on them.
Run them when titles are added; each leaves a row that is already filled alone unless
you pass `--force`. `fetch_years.py` searches for nothing — it reads the store pages
`data/covers.csv` already records, so a title with no packshot has no year from it
either, and that year is filled in by hand.

## Where the covers come from

The packshot is Steam's portrait capsule, 600×900, converted to WebP at 300×450 and
600×900 — Steam's own two sizes, so nothing is upscaled. It is the PC key art, not
the PSN packshot: the PlayStation Store renders search client-side behind a rotating
query hash, which no script here can reach without driving a browser. Every row in
`data/covers.csv` records the store page its image came from, which is why a file
without a source is refused outright.

139 of the 168 games have one. The other 29 are titles Steam does not carry, or
carries without a portrait capsule — the annual sports games, the PlayStation
exclusives, Diablo III, a few delisted ones — and they keep the generated
typographic card.
That split is printed on every run, and the matching is deliberately strict: the
store's name has to equal the catalogue's name once typography is stripped, or the
id has to be listed in the script's `ALIASES` with a reason. A cover is what a
reader recognises before they read the title, so a wrong one is worse than a blank.

| File | What it holds |
| --- | --- |
| `data/source-list.txt` | The received list, verbatim. Provenance, never corrected. |
| `data/canonical.csv` | Franchise and bundle names resolved to real products, or dropped. |
| `data/excluded.csv` | Real PS5 games the inclusion rule keeps out, and why each one. |
| `data/coop.csv` | Players, screen type and what the co-op covers. |
| `data/catalog.csv` | Genre, release year and publisher. |
| `data/covers.csv` | Packshots and where each came from. |

A blank in a worksheet means *nobody has established this yet*. It never means zero,
and nothing invents a value to fill it — an unknown player count is left unknown,
because a wrong one sends somebody to buy the wrong game.

There are none left. Every one of the 168 entries carries a player count, a screen
mode, a scope and a genre, so **CI validates with `--strict`** and a blank now fails
the publish rather than being counted and shipped. Run `validate_dataset.py --strict`
before pushing to see what CI will say; the plain run still just prints the count,
which is what you want while a new title is half filled in.

## Proposing a game

Open an issue or a pull request with the title as the PlayStation Store spells it,
and say **how many people can play on one console and whether the screen splits**.
That is the part nobody can look up quickly, and a proposal without it cannot be
filed.

Check it against the inclusion rule first — online-only co-op is the one that comes
up every time, and `data/excluded.csv` already lists the twelve games turned away for
it, so look there before writing the issue. If co-op is limited to one mode, say which.

To add it yourself: put the title in `data/source-list.txt`, fill its row in
`data/coop.csv` and `data/catalog.csv`, then run the three scripts above.

## The roadmap

`docs/ROADMAP.md`, `docs/CHANGELOG.md` and `docs/IMPROVEMENTS.md` are owned by the
[roadkeep](https://pypi.org/project/roadkeep/) CLI and are never edited by hand — a
hook in this repository refuses it. Use `roadkeep brief` to start a task and
`roadkeep ship` to close one.
