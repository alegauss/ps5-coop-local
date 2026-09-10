# Roadmap (active backlog)

## Block A — Game data

- ⏳ **CL3** (deps: —) **no title says how many players fit on the couch, or whether the screen splits or is shared** — 58 titles still carry no player count or screen mode, so the couch question stays unanswerable for them until somebody checks the store. → §CL3
- ⏳ **CL4** (deps: —) **games carry no genre, year or publisher, so there is no axis to group the grid by** — 14 titles have no genre the ten labels honestly fit, year is blank throughout, and 111 titles still have no publisher. → §CL4
- ⏳ **CL5** (deps: —) **entries like 'Bleed 1 e 2', 'Trine Series' and 'King of Fighters' name a collection, not a game** — Diablo III e IV still names two products at once, and Minigolf, Runner and TOGETHER match no store listing anybody has checked yet. → §CL5
- ⏳ **CL6** (deps: —) **no game has cover art, and a game grid without art is a text table** — No game has a real packshot yet, so all 184 covers are the generated fallback and a licensed image source still has to be chosen. → §CL6

## Block B — Catalog site

## Block C — Publishing and docs

- ⏳ **CL19** (deps: CL7 ✅) **the site is published nowhere, so the list exists only on the developer's machine** — Pages still has to be switched to the GitHub Actions source in repository settings, which no workflow file can do, and this branch has to reach main. → §CL19
- 📋 **CL20** (deps: —) **the repository never says what the project is, where the list came from, or how to run it** — With no README a cloner cannot tell a site from a dataset from a scratch note. → §CL20
- 📋 **CL21** (deps: CL1 ✅) **nothing validates the dataset: broken JSON or a missing field surfaces in the user's browser** — A static site has no server to catch bad data, so it has to be refused before shipping. → §CL21

## Block D — Visual design and polish

## Done when — Block A

- **Every entry is a real PS5 product** No duplicate id, no franchise name standing in
  for a game, and every title findable on the PSN store.
- **Player count and screen mode on every game** The validator refuses a record missing
  either field, so the grid can always render the badge.

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

## Non-goals

- **Online-only coop** A game whose coop needs a second console or a PSN session is out;
  the whole point of this list is two to four people on one couch, one PS5.
- **Prices, stores and buy links** Prices go stale within a week and would turn a
  reference into a storefront that has to be maintained against the PSN sales calendar.
- **Other platforms** No PS4, Switch or PC entries, even where the same game has local
  coop there: one platform keeps every player-count and screen-mode claim verifiable.
- **User accounts, ratings and comments** A catalog that needs a backend stops being a
  static page anyone can fork, and moderation is a cost this project will not carry.
