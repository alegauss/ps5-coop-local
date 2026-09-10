# Improvements

## Block A — Game data

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
