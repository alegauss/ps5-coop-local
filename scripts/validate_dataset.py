#!/usr/bin/env python3
"""Refuse a broken catalogue before it reaches a browser.

A static site has no server to catch bad data at request time: whatever is in
data/games.json is what the grid renders, and a missing field surfaces as a hole
on someone's phone. This is the only defence that arrangement allows, so it runs
in the repository and in CI rather than anywhere clever.

Two levels, deliberately
------------------------
**Errors** are corruption -- a repeated id, a record with no name, a genre outside
the vocabulary, a player count below two, a cover pointing at a file that is not
there. Any of them fails the run.

**Gaps** are facts nobody has established yet. CL3 and CL4 left blanks on purpose,
because a blank is honest where a guess would not be, and the run prints how many
rather than quoting a number here that would be wrong a commit later. They do not
fail the run -- otherwise the gate could only be adopted by first inventing the data
it exists to protect.

A gap is not the same as a game that does not belong. An entry whose co-op needs a
network has no honest player count to be missing: it is in data/excluded.csv and never
reaches this file at all.

``--strict`` promotes every gap to an error, and CI throws it (CL24): the curation
is finished, so every one of the 168 records carries a player count, a screen mode,
a scope and a genre. A blank is therefore no longer a fact nobody has established --
it is a regression, and the publish fails on it.

The plain run stays the default because it is the useful one while a title is being
added: it prints what is still open instead of refusing to build. Run it with
--strict before pushing and you learn what CI is about to say.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATASET = ROOT / "data" / "games.json"

# Present and non-empty on every record, always.
REQUIRED = ("id", "name", "cover")

# Present once the curation behind them is finished; see --strict.
COMPLETENESS = ("max_players", "screen", "scope", "genre")

# Kept in step with GENRES in build_dataset.py on purpose: the builder refuses a typo
# on the way in, and this refuses one that reached the committed file some other way.
GENRES = {
    "beat-em-up", "platformer", "party", "shooter", "rpg",
    "sports", "racing", "puzzle", "survival", "fighting",
    "adventure", "simulation",
}
SCREENS = {"split", "shared", "pass"}
SCOPES = {"campaign", "side", "versus"}

# A local co-op catalogue listing a game for one player is a contradiction, not a
# datum: two is the floor by definition.
MIN_PLAYERS = 2


def check(dataset: dict, strict: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    gaps: list[str] = []

    games = dataset.get("games")
    if not isinstance(games, list) or not games:
        return ["games is missing or empty"], []

    count = dataset.get("count")
    if count != len(games):
        errors.append(f"count says {count} but there are {len(games)} records")

    seen: dict[str, int] = {}
    for index, game in enumerate(games):
        where = game.get("id") or f"record {index}"

        for field in REQUIRED:
            if not game.get(field):
                errors.append(f"{where}: missing {field}")

        game_id = game.get("id")
        if game_id:
            if game_id in seen:
                errors.append(f"{where}: id repeated (also record {seen[game_id]})")
            seen[game_id] = index

        genre = game.get("genre")
        if genre is not None and genre not in GENRES:
            errors.append(f"{where}: genre {genre!r} is outside the vocabulary")

        screen = game.get("screen")
        if screen is not None and screen not in SCREENS:
            errors.append(f"{where}: screen {screen!r} is outside the vocabulary")

        scope = game.get("scope")
        if scope is not None and scope not in SCOPES:
            errors.append(f"{where}: scope {scope!r} is outside the vocabulary")

        players = game.get("max_players")
        if players is not None and (not isinstance(players, int) or players < MIN_PLAYERS):
            errors.append(f"{where}: max_players is {players!r}, below {MIN_PLAYERS}")

        for field in ("cover", "cover_2x"):
            path = game.get(field)
            if path and not (ROOT / path).is_file():
                errors.append(f"{where}: {field} points at {path}, which is not there")

        for field in COMPLETENESS:
            if game.get(field) in (None, ""):
                (errors if strict else gaps).append(f"{where}: no {field}")

    return errors, gaps


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--strict",
        action="store_true",
        help="treat an unfilled field as an error, not a gap -- what CI runs, so a "
             "blank field fails the publish instead of shipping a hole",
    )
    args = parser.parse_args()

    if not DATASET.exists():
        print(f"validate: {DATASET} is not there; run build_dataset.py", file=sys.stderr)
        return 1
    try:
        dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"validate: {DATASET.name} is not valid JSON: {exc}", file=sys.stderr)
        return 1

    errors, gaps = check(dataset, args.strict)

    for message in errors:
        print(f"validate: ERROR {message}", file=sys.stderr)
    if gaps:
        print(
            f"validate: {len(gaps)} field(s) not yet established across "
            f"{len({g.split(':')[0] for g in gaps})} record(s) -- run --strict to refuse them",
            file=sys.stderr,
        )
    if errors:
        print(f"validate: {len(errors)} error(s)", file=sys.stderr)
        return 1

    print(f"validate: {len(dataset['games'])} record(s), clean", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
