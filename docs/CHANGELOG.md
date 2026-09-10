# Shipped Ledger

## Block A — Game data

- ✅ **CL1** **the game list exists only as pasted text, with no data file the interface can read** — Every pasted entry is now a record in data/games.json, with a derived stable id and the source's caveat kept, so a screen can read the catalog (design recorded in `scripts/build_dataset.py`).
- ✅ **CL2** **the list repeats titles and mixes variants of the same game, and nothing reconciles them** — The 195 source lines are now 188 entries, one per product, and every folded title stays in aliases so search still matches what the source said (design recorded in `scripts/build_dataset.py`).

## Block B — Catalog site

## Block C — Publishing and docs

## Block D — Visual design and polish

