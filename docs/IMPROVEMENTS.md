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

## Block B — Catalog site

## Block C — Publishing and docs

### §CL24 Turning the validator strict

validate_dataset.py has had --strict since CL21 and nothing runs it. The switch promotes
every gap -- max_players, screen, scope, genre -- from a printed count to a refusal, and
its own docstring says it is the switch to throw once the curation is finished. It
nearly is: CL3 closed player count and screen, CL23 closed genre, and one field is left
in the whole dataset -- Guts 'N Goals, with no scope.

That one blank matters less than what it stands for. The filters are built from the
data: app.js offers one genre chip per value present, and passesFilters drops a game
whose field does not equal the active chip. So a null field does not merely leave a game
unlabelled, it hides it the moment anyone filters, and nothing on the page says so.
Today nothing can vanish. The next title added without a scope can, and CI would publish
it.

Two steps, and the order is the point:

- Establish the Guts 'N Goals scope. It is four players on a shared screen with the scope
  open, because the sources disagreed on whether its co-op is a mode of its own or only
  versus with AI teammates.
- Add --strict to the validate step in .github/workflows/pages.yml, so a record missing a
  field fails the publish instead of shipping a hole.

Reversing them turns the gate into a blocked branch: --strict first fails the build on a
field nobody has established yet.

On ship: --recorded-in scripts/validate_dataset.py.

## Block D — Visual design and polish
