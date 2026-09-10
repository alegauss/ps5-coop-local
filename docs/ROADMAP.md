# Roadmap (active backlog)

## Block A — Game data

## Block B — Catalog site

## Block C — Publishing and docs

## Block D — Visual design and polish

## Done when — Block A

- **Every entry is a real PS5 product** No duplicate id, no franchise name standing in
  for a game, and every title findable on the PSN store.
- **Player count and screen mode on every game** The validator refuses a record missing
  either field, so the grid can always render the badge.
- **every entry can be played by two people on one console** The rule the catalogue
  exists for. A game whose co-op needs a network belongs in data/excluded.csv with its
  reason, never in the grid behind a blank player count. Checked by build_dataset.py,
  which refuses an excluded id it cannot find, so a rename can never quietly readmit
  one.

## Done when — Block B

- **Any game reachable in under three seconds** Typing three letters, or one filter,
  narrows two hundred titles to a visible handful.
- **Usable with keyboard alone and on a phone** Full traversal with no mouse, and the
  same grid readable in two columns at 390 pixels.

## Done when — Block D

- **The grid reads as a shelf, not a spreadsheet** Cover art carries the page, one
  accent color, and the player badge legible at arm's length.

## Done when — Block C

- **A public link that opens fast on mobile data** Published from main with no build
  step, and the grid usable before the last cover lands.
- **the page depends on nothing outside this repository** No CDN, no web font, no
  analytics, no API. The grid has to render from files this repository serves, so a
  visitor on a phone network waits on one origin and nothing a third party does can
  break the page. Checked by reading index.html and assets/site for an off-origin URL.
- **a record with a blank field fails the publish** The curation is finished, so a gap
  is a regression rather than an unfilled fact, and an unfilled field silently drops a
  game out of every filtered view. Checked by the validate step in
  .github/workflows/pages.yml carrying --strict.

## Non-goals

- **Online-only coop** A game whose coop needs a second console or a PSN session is out;
  the whole point of this list is two to four people on one couch, one PS5.
- **Prices, stores and buy links** Prices go stale within a week and would turn a
  reference into a storefront that has to be maintained against the PSN sales calendar.
- **Other platforms** No PS4, Switch or PC entries, even where the same game has local
  coop there: one platform keeps every player-count and screen-mode claim verifiable.
- **User accounts, ratings and comments** A catalog that needs a backend stops being a
  static page anyone can fork, and moderation is a cost this project will not carry.
