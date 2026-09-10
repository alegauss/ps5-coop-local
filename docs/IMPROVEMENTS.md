# Improvements

## Block A — Game data

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
