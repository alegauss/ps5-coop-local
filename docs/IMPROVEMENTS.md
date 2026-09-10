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
vocabulary becomes thirty labels holding one game each and filters nothing. Publisher
comes along because it sorts and gives context without costing another curation call.

Year was defined as the PS5 release year, and that is the one thing here that turned out
wrong. It cost a curation call nobody could make: most of this list is PS4 software
played through back-compat and has no PS5 date, so the column was null on all 184
records while the site shipped a "Newest first" sort and a "Released" row against it. It
now means the year the game came out, the product a row names in its earliest form,
which is the same axis and is sourceable -- scripts/fetch_years.py reads the store pages
data/covers.csv already records, and names the seventeen where the listing's date is not
the product's.

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

CL5 has since renamed Orcs Must Die! to Orcs Must Die! 3, the id to drop, and confirmed
Samurai Gunn 2 shipped on PS5. None of the twelve waits on a name.

On ship: --recorded-in data/canonical.csv, plus a criterion naming the inclusion rule.

### §CL23 A genre label for the games that fit none

The ten labels were closed on purpose and CL4 shows the cost: with 179 of 184 entries
placed, three games still have no home. A Way Out is a co-op cinematic adventure, Arcade
Paradise an arcade management sim around retro mini-games, CrossKrush a two-player
demolition puzzle. The other two blanks, Runner and TOGETHER, are CL5 names.

The design that closed the vocabulary is right about why: an open list becomes thirty
labels holding one game each and filters nothing. But a blank is not free either. The
grid groups by genre, so an unlabelled game is in no group at all -- worse than being
filed imperfectly, because a reader who filters never sees it.

Three exits:

- One or two labels that earn their place, "adventure" the obvious candidate, chosen by
  counting how many existing entries would move.
- A single "other" label, keeping ten real genres and putting the leftovers where a filter
  can still reach them.
- Keep the blank and make the grid show it, which is a Block B rendering decision and
  belongs on its own line there, not here.

The first two are a worksheet edit plus GENRES in scripts/build_dataset.py.

On ship: --recorded-in scripts/build_dataset.py.

## Block B — Catalog site

## Block C — Publishing and docs

## Block D — Visual design and polish
