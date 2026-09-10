# Roadmap (active backlog)

## Block A — Game data

- ⏳ **CL3** (deps: CL22, CL5 ✅) **no title says how many players fit on the couch, or whether the screen splits or is shared** — 13 titles are left: the 12 CL22 will drop for having no local coop, and NHL 21, whose local player count no listing states. → §CL3
- ⏳ **CL4** (deps: CL23) **games carry no genre, year or publisher, so there is no axis to group the grid by** — 8 years, 3 genres and 2 publishers are open; the genres are the three CL23 has to label, and the rest are fields no listing checked here answers. → §CL4
- 📋 **CL22** (deps: —) **twelve entries have no local coop at all, and a blank player count reads as not yet checked** — Returnal, Fall Guys, Astroneer and nine more are online-only or single-player, so the catalogue advertises games that fail its own inclusion rule. → §CL22
- 📋 **CL23** (deps: —) **three real games fit none of the ten genre labels, so the grid leaves them out of every filter** — A Way Out is a coop cinematic adventure and Arcade Paradise an arcade management sim; calling either a platformer files it where nobody would look for it. → §CL23

## Block B — Catalog site

## Block C — Publishing and docs

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
- **the page depends on nothing outside this repository** No CDN, no web font, no
  analytics, no API. The grid has to render from files this repository serves, so a
  visitor on a phone network waits on one origin and nothing a third party does can
  break the page. Checked by reading index.html and assets/site for an off-origin URL.

## Done when — CL3

- **max players and screen mode on every entry, or the entry is gone** build_dataset.py
  prints the coverage on every run, so the check is that its "still blank" count reaches
  zero. The 18 left do not close with a number: twelve are games with no local coop and
  five name no product, and both of those close by removal.

## Done when — CL4

- **a genre and a publisher on every entry, and the year column settled**
  build_dataset.py prints genre coverage on every run, so that half is counted. Year is
  the open question rather than a gap: it means the PS5 release year, and a PS4 title
  played through back-compat has none, so what finishes this is the column being filled
  or dropped, not left silently empty.

## Non-goals

- **Online-only coop** A game whose coop needs a second console or a PSN session is out;
  the whole point of this list is two to four people on one couch, one PS5.
- **Prices, stores and buy links** Prices go stale within a week and would turn a
  reference into a storefront that has to be maintained against the PSN sales calendar.
- **Other platforms** No PS4, Switch or PC entries, even where the same game has local
  coop there: one platform keeps every player-count and screen-mode claim verifiable.
- **User accounts, ratings and comments** A catalog that needs a backend stops being a
  static page anyone can fork, and moderation is a cost this project will not carry.
