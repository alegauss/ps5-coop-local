# Shipped Ledger

## Block A — Game data

- ✅ **CL1** **the game list exists only as pasted text, with no data file the interface can read** — Every pasted entry is now a record in data/games.json, with a derived stable id and the source's caveat kept, so a screen can read the catalog (design recorded in `scripts/build_dataset.py`).
- ✅ **CL2** **the list repeats titles and mixes variants of the same game, and nothing reconciles them** — The 195 source lines are now 188 entries, one per product, and every folded title stays in aliases so search still matches what the source said (design recorded in `scripts/build_dataset.py`).
- ✅ **CL3 (130 of 188 titles)** **no title says how many players fit on the couch, or whether the screen splits or is shared** — data/coop.csv gives max players, screen mode and scope for 130 of 188 titles, under a closed vocabulary the builder refuses to widen.
- ✅ **CL4 (genre on 174 of 188 titles)** **games carry no genre, year or publisher, so there is no axis to group the grid by** — data/catalog.csv gives one genre from a closed ten-label vocabulary for 174 of 188 titles, plus publisher for 77, so the grid has an axis to group by.
- ✅ **CL5 (9 of the collection names)** **entries like 'Bleed 1 e 2', 'Trine Series' and 'King of Fighters' name a collection, not a game** — data/canonical.csv resolves nine franchise and bundle names to the product PS5 sells, or drops one that exists only inside an emulation collection.
- ✅ **CL6 (the generated fallback cards)** **no game has cover art, and a game grid without art is a text table** — Every game has a 2:3 cover: a typographic card in its genre colour, served locally, plus a worksheet where a real packshot lands with its source.

## Block B — Catalog site

- ✅ **CL7** **there is no page at all: the repository holds no site that shows the catalog** — The catalogue renders: a static page with no framework or build step reads games.json and lays all 184 titles out as one scrolling grid of cover cards (design recorded in `assets/site/app.js`).
- ✅ **CL8** **with nearly two hundred titles on one page, finding a game means scrolling or Ctrl+F** — Filters on every keystroke across names and aliases, folding case, accents and punctuation, tolerating one typo; the query lives in the URL (design recorded in `assets/site/app.js`).
- ✅ **CL9** **there is no way to filter by player count, genre or screen type** — Players, genre and screen filter the grid together, each reversible, all three carried in the URL, and a game whose value is unknown never satisfies a filter (design recorded in `assets/site/app.js`).

## Block C — Publishing and docs

## Block D — Visual design and polish

