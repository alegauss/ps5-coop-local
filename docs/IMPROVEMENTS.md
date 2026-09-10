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

### §CL22 Entries with no local coop

CL3 went looking for player counts and found twelve entries where the answer is not a
number. Nine have coop that needs the network -- Astroneer, Fall Guys, GRAVEN, Orcs Must
Die!, Returnal, Super Bomberman R Online, Ultimate Fishing Simulator 2, Vermintide 2,
Worms Rumble -- and three have no second player at all: Disney Classic Games, Omega
Strike, Rogue Legacy 2. Ultimate Fishing Simulator 2 is the weakest read, from a store
page advertising multiplayer only "via the Internet".

"Online-only coop" is already a non-goal and the README states the rule first: two or
more people, one console, one television. So these twelve are not gaps in the data, they
are entries the rule excludes -- and leaving max_players blank claims the opposite,
since a blank means nobody has established this yet.

The exit is the drop action in data/canonical.csv, which already removes a line whose
game is not a PS5 product; this is the same removal for a different reason, and
data/source-list.txt keeps the original claim either way. What has to be settled first
is whether a silent drop is enough, because the next person to paste a list will propose
Fall Guys again and a removal that records no reason teaches them nothing.

Note Orcs Must Die! also names the series rather than a product, so CL5 reaches it too;
the drop and the rename must not both fire on one line.

On ship: --recorded-in data/canonical.csv, plus a criterion naming the inclusion rule.

## Block B — Catalog site

## Block C — Publishing and docs

### §CL19 Publishing

GitHub Pages from the main branch, with no build step, because the site is static by
decision. Every push publishes. The link is the product: it has to open fast on a phone
network and depend on nothing outside the repository.

## Block D — Visual design and polish
