# Shipped Ledger

## Block A — Game data

- ✅ **CL1** **the game list exists only as pasted text, with no data file the interface can read** — Every pasted entry is now a record in data/games.json, with a derived stable id and the source's caveat kept, so a screen can read the catalog (design recorded in `scripts/build_dataset.py`).
- ✅ **CL2** **the list repeats titles and mixes variants of the same game, and nothing reconciles them** — The 195 source lines are now 188 entries, one per product, and every folded title stays in aliases so search still matches what the source said (design recorded in `scripts/build_dataset.py`).
- ✅ **CL3** **no title says how many players fit on the couch, or whether the screen splits or is shared** — All 168 entries now state max players and screen mode, so the couch question is answerable for every game in the grid (design recorded in `scripts/build_dataset.py`).
- ✅ **CL4 (179 genres, 177 publishers, 170 years)** **games carry no genre, year or publisher, so there is no axis to group the grid by** — data/catalog.csv gives genre for 179 of 184, publisher for 177 and year for 170, the year sourced from the store pages covers.csv already records.
- ✅ **CL5** **entries like 'Bleed 1 e 2', 'Trine Series' and 'King of Fighters' name a collection, not a game** — data/canonical.csv resolves every questioned name: one line splits into two products, five entries PS5 does not sell are dropped, three are renamed (design recorded in `scripts/build_dataset.py`).
- ✅ **CL6** **no game has cover art, and a game grid without art is a text table** — 148 of 184 games now carry a real 2:3 WebP packshot at Steam's own two sizes, attributed to its store page; the other 36 keep the generated card (design recorded in `scripts/fetch_covers.py`).
- ✅ **CL22** **twelve entries have no local coop at all, and a blank player count reads as not yet checked** — data/excluded.csv keeps twelve real PS5 games out with a reason each, kept apart from canonical.csv because these fail the rule, not their name (design recorded in `data/excluded.csv`).

## Block B — Catalog site

- ✅ **CL7** **there is no page at all: the repository holds no site that shows the catalog** — The catalogue renders: a static page with no framework or build step reads games.json and lays all 184 titles out as one scrolling grid of cover cards (design recorded in `assets/site/app.js`).
- ✅ **CL8** **with nearly two hundred titles on one page, finding a game means scrolling or Ctrl+F** — Filters on every keystroke across names and aliases, folding case, accents and punctuation, tolerating one typo; the query lives in the URL (design recorded in `assets/site/app.js`).
- ✅ **CL9** **there is no way to filter by player count, genre or screen type** — Players, genre and screen filter the grid together, each reversible, all three carried in the URL, and a game whose value is unknown never satisfies a filter (design recorded in `assets/site/app.js`).
- ✅ **CL10** **the grid has no ordering: not alphabetical, not by year, not by player count** — Alphabetical by default and ignoring a leading article, plus newest first and most players first, with unknown values sorted last rather than as zero (design recorded in `assets/site/app.js`).
- ✅ **CL11** **opening a game leads nowhere: no detail view with its coop mode and the list's caveats** — A side panel carries the cover, players, screen, scope and genre, and surfaces the source's caveat that Zombies or split screen is the only co-op (design recorded in `assets/site/app.js`).
- ✅ **CL12** **the page never says how many games exist, or how many survived the current filter** — A live count sits above the grid and moves with every filter: 184 games unfiltered, 9 of 184 when the filters narrow it, announced to a screen reader (design recorded in `assets/site/app.js`).
- ✅ **CL13** **the layout is unverified on phones, which is where the list gets read in front of the TV** — Two columns at 390px, search pinned while scrolling, filters in a sheet rising from the bottom, 44-pixel touch targets and a full-screen detail panel (design recorded in `assets/site/styles.css`).
- ✅ **CL14** **without a mouse nothing works: search never takes focus and the grid cannot be traversed** — Slash jumps to search, a skip link opens the tab order, one visible focus ring throughout, and Enter opens a card that Escape closes (design recorded in `assets/site/styles.css`).

## Block C — Publishing and docs

- ✅ **CL19** **the site is published nowhere, so the list exists only on the developer's machine** — https://alegauss.github.io/ps5-coop-local/ is live, and the grid loads from an 88 KB games.json and a 24 KB app.js with the covers lazy.
- ✅ **CL21** **nothing validates the dataset: broken JSON or a missing field surfaces in the user's browser** — A validator refuses a repeated id, a missing field, an off-vocabulary genre, a player count below two, and a cover that is not there (design recorded in `scripts/validate_dataset.py`).
- ✅ **CL20** **the repository never says what the project is, where the list came from, or how to run it** — A README states what the catalogue is, the one-console rule that settles the online argument, where the list came from, and how to run it in one line (design recorded in `README.md`).

## Block D — Visual design and polish

- ✅ **CL15** **the site has no identity: with no palette, type scale or grid it reads as a test page** — A blue-black ground with near-neutral chrome, one accent on focus, active filters and the count, a four-step type scale and spacing in eights (design recorded in `assets/site/styles.css`).
- ✅ **CL16** **the grid cannot tell two-player coop from four-player, and that is what decides the night** — Each cover carries a corner badge with the player count and a bar for screen type, only where the count is known and never dependent on hover (design recorded in `assets/site/app.js`).
- ✅ **CL17** **a search that matches nothing returns a blank screen explaining nothing** — An empty result names what emptied the list and offers the way back: the nearest title, dropping the narrowest filter, or clearing everything (design recorded in `assets/site/app.js`).
- ✅ **CL18** **loading all 190 covers at once delays the first paint of the grid** — The first sixteen covers load eagerly at high priority and the rest lazily, with every box declared so the grid never jumps as images land (design recorded in `assets/site/app.js`).
