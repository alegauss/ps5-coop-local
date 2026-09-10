# Improvements

## Block A — Game data

### §CL3 Couch-coop metadata

Local coop is not one field. Each game needs max players on a single console, screen
mode (split, shared or pass-the-controller) and scope (full campaign, side modes only,
versus only). Streets of Rage 4 and Overcooked are both four-player coop and play
nothing alike; the grid has to say which is which before the click.

### §CL4 Grouping axes

One genre per game, from a closed and deliberately small vocabulary: beat 'em up,
platformer, party, shooter, RPG, sports, racing, puzzle, survival, fighting. An open
vocabulary becomes thirty labels holding one game each and filters nothing. PS5 release
year and publisher come along because they sort and give context without costing another
curation call.

### §CL5 Canonical names

About a dozen entries name a franchise or a bundle instead of a product: Bleed 1 e 2,
Trine Series, King of Fighters, Street Fighter, Bomberman, Final Fight, Minigolf, Quake,
Spelunky. Each resolves to the exact title sold on PS5 — Trine 4, The King of Fighters
XV — or drops out, when all that exists is emulation inside another collection.

### §CL6 Cover art

Covers in 2:3 portrait, the PS5 packshot ratio, served locally as WebP so no third-party
domain can move the path out from under the page. Where no art exists, a typographic
card with the initials and the genre color — better than a gray rectangle, and it keeps
the grid aligned. Each image records where it came from.

## Block B — Catalog site

### §CL11 Game detail

A side panel, not a new page: the grid stays behind it and closing costs no navigation.
It carries the large cover, players, screen type, genre, year and the caveat in prose —
Call of Duty is local coop only in Zombies, Mortal Kombat 11 only in Towers of Time, WRC
Generations only in split screen. This is what the source list carried in parentheses
and nothing else has kept.

### §CL12 The count

A number next to the search, moving with the filters: 187 games, 41 games for four. It
is the cheapest possible feedback that the interaction landed, and it is also what gives
a newcomer the scale of the catalog.

### §CL13 Phone reading

Two cover columns on a phone, search pinned to the top while scrolling, filters in a
sheet that rises from the bottom. Touch targets at 44 pixels, no information carried by
hover, and the detail panel taking the full screen. This is the primary device, not the
adaptation.

### §CL14 Keyboard access

Focus order following the reading order, a focus ring visible against the dark ground,
slash as the shortcut to search and Escape closing the detail panel. The grid is a
semantic list whose game names are real text, not baked into the image — screen readers
and the browser's own find depend on that.

## Block C — Publishing and docs

### §CL19 Publishing

GitHub Pages from the main branch, with no build step, because the site is static by
decision. Every push publishes. The link is the product: it has to open fast on a phone
network and depend on nothing outside the repository.

### §CL20 README

What it is, the inclusion rule — local coop on one PS5 console —, where the list came
from, how to run it in one line, and how to propose a game. The inclusion rule is the
part that heads off the recurring argument about online coop, which is precisely what
this catalog is not.

### §CL21 Catalog validation

A checker that runs in the repository and refuses: a repeated id, a missing required
field, a genre outside the vocabulary, a player count below two, and cover art pointing
at a file that is not there. It runs before commit and in CI. It costs little and it is
the only defense a backend-less site has against its own data.

## Block D — Visual design and polish

### §CL15 Visual language

A dark blue-black ground, the tone of the console's own interface, with cover art as the
only saturated color on screen — game art is loud already and fights any palette put
beside it. A narrow sans for long titles inside small cards, a four-step type scale and
spacing in multiples of eight. One accent color, spent on focus, active filters and the
count, and nowhere else.

### §CL16 Player badge

A badge in the corner of each cover with the player count, plus a color bar for screen
type. Readable at arm's length with a phone in hand, never dependent on hover, and never
covering the title inside the art. It is the only thing the grid adds on top of a cover,
which is why it has to earn the space it takes.

### §CL17 Empty state

When nothing matches, say which combination emptied the list and offer the way back:
drop the narrowest filter, or clear everything. If the search only just missed, suggest
the nearest title. This is the ordinary case of filtering five players and a niche genre
at once.

### §CL18 Image cost

Lazy loading below the fold, declared dimensions on every card so the grid does not jump
when an image lands, and covers in two sizes served by screen density. The first visible
covers get priority; the rest can arrive as the page scrolls. The target is a usable
grid before the last image.
