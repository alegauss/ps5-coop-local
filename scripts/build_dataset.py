#!/usr/bin/env python3
"""Turn data/source-list.txt into data/games.json.

Why this exists
---------------
The catalog arrived as pasted text. Text is a source, not a format: nothing can
sort, filter or count it, so every screen in Block B needs one record per entry
before it can read anything. This script is that conversion, and the source file
stays versioned beside its output as the provenance for every record.

What it does NOT do
-------------------
The conversion is mechanical on purpose. It parses; it does not curate:

* ``cover`` is emitted as null (CL6). The schema carries it from the first commit
  so the readers can be written against a stable shape, but a value invented here
  would be a guess wearing the costume of data.

What the source puts in parentheses is kept verbatim in ``source_note`` -- the
"(modo Zombies)" and "(Tela dividida)" caveats are what CL11 surfaces, and they
would be lost if the title were simply cleaned.

Reconciliation (CL2)
--------------------
One entry per buyable PS5 product. Two lines that slugify to the same id are the
same entry and collapse on their own; the pairs that do not are a judgement about
what the store actually sells, so they are named in ``MERGES`` rather than guessed
at by string distance -- "Wonderland" and "Wonderlands" are one typo apart and
"Salt and Sacrifice" and "Salt and Sanctuary" are two different games.

Nothing is discarded by a merge. Every folded title stays in ``aliases``, because
the source spelling is what somebody will type into the search box.

Couch-coop metadata (CL3)
-------------------------
``max_players``, ``screen`` and ``scope`` come from ``data/coop.csv``, a worksheet
carrying one row per id so the unanswered ones are visible rather than absent. The
vocabulary is closed and checked on read: a screen or scope outside it is a typo,
and a typo reaching the grid renders a badge nobody can filter on.

A blank stays null. Local coop is not one field -- Streets of Rage 4 and Overcooked
are both four players and play nothing alike -- and the number here is what decides
a purchase, so an unverified entry is left for somebody with the store open rather
than filled with a plausible guess.

Grouping axes (CL4)
-------------------
``genre``, ``year`` and ``publisher`` come from ``data/catalog.csv``, read the same
way. Genre is one label from a closed set of ten, checked on read for the same
reason the coop vocabulary is: an open vocabulary becomes thirty labels holding one
game each, and filters nothing.

``year`` was the PS5 release year, and that definition is why it sat blank on all 184
records: most of this list is PS4 software played through back-compat and has no PS5
release date to carry, so the honest value was nothing, permanently -- for a column
the site already sorted by. It now means the year the game came out, the product a
row names in its earliest form, which is the same "how old is this" axis and can
actually be sourced. ``scripts/fetch_years.py`` does most of it, from the store pages
``data/covers.csv`` already records.

One gap is still deliberate. A handful of titles have no genre because the ten labels
have no honest home for them: "A Way Out" is a co-op cinematic adventure, and calling
it a platformer to avoid a blank would put it under a filter nobody would find it in.

Canonical names (CL5)
---------------------
About a dozen source lines name a franchise or a bundle rather than a product, and a
non-canonical name matches no cover, no store listing and nothing the user types.
``data/canonical.csv`` resolves them: a rename recomputes the id from the new title,
and a drop removes a line whose game exists on PS5 only inside an emulation
collection.

The source spelling always survives as an alias -- "King of Fighters" is what
somebody will type long after the record says The King of Fighters XV. Where the
canonical title already has its own entry, the two arrive at the same id and the
reconciliation above folds them, so this file never has to know which case it is in.
"""

from __future__ import annotations

import csv
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "source-list.txt"
COOP = ROOT / "data" / "coop.csv"
CATALOG = ROOT / "data" / "catalog.csv"
CANONICAL = ROOT / "data" / "canonical.csv"
COVERS = ROOT / "data" / "covers.csv"
TARGET = ROOT / "data" / "games.json"

SCHEMA_VERSION = 1

# The generated fallback card, which every game has until a packshot replaces it.
GENERATED_COVER = "assets/covers/{id}.svg"

# One genre per game, closed on purpose (CL4): an open vocabulary becomes thirty
# labels holding one game each, which filters nothing.
GENRES = {
    "beat-em-up", "platformer", "party", "shooter", "rpg",
    "sports", "racing", "puzzle", "survival", "fighting",
}

# The couch-coop vocabulary (CL3). A value outside these sets is a typo in the
# worksheet, and a typo that reaches the grid renders a badge nobody can filter on.
SCREENS = {"split", "shared", "pass"}
SCOPES = {"campaign", "side", "versus"}

# A trailing "(...)" is the source's caveat about the entry, not part of its title.
TRAILING_PAREN = re.compile(r"\s*\(([^()]*)\)\s*$")

# Two lines that are one product under two names: the id that survives -> the ids
# folded into it. The survivor is the title the PS5 store sells, which is why this
# is a list and not a heuristic. Exact repeats need no entry here -- identical ids
# collapse on their own. A stale entry is an error, not a silent no-op.
MERGES = {
    "tiny-tinas-wonderlands": ["tiny-tinas-wonderland"],
    "the-dark-pictures-anthology-house-of-ashes": ["house-of-ashes"],
    "outward-definitive-edition": ["outward"],
}


def slugify(name: str) -> str:
    """A stable, url-safe id derived from the title alone.

    Derived rather than assigned so that re-running this script never renumbers a
    record: the id of a line is a function of its text and nothing else.
    """
    decomposed = unicodedata.normalize("NFKD", name)
    ascii_only = "".join(c for c in decomposed if not unicodedata.combining(c))
    lowered = ascii_only.lower().replace("'", "").replace("’", "")
    return re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9]+", "-", lowered)).strip("-")


def read_rows(path: Path) -> list[dict]:
    """A worksheet's data rows, with the leading `#` commentary stripped."""
    if not path.exists():
        return []
    text = "\n".join(
        line for line in path.read_text(encoding="utf-8").splitlines()
        if not line.lstrip().startswith("#")
    )
    return list(csv.DictReader(text.splitlines()))


def read_canonical(path: Path) -> dict[str, dict]:
    """The franchise-and-bundle rules, keyed by the id the raw source line derives."""
    rules: dict[str, dict] = {}
    for row in read_rows(path):
        game_id = (row.get("id") or "").strip()
        if not game_id:
            continue
        action = (row.get("action") or "").strip()
        value = (row.get("value") or "").strip()
        if action not in {"rename", "drop"}:
            raise ValueError(f"{path.name}: {game_id} has action {action!r}, not rename or drop")
        if action == "rename" and not value:
            raise ValueError(f"{path.name}: {game_id} is a rename with no title to rename to")
        if action == "drop" and value:
            raise ValueError(f"{path.name}: {game_id} is a drop and cannot carry a title")
        rules[game_id] = {"action": action, "value": value}
    return rules


def apply_canonical(games: list[dict], rules: dict[str, dict]) -> list[dict]:
    """Resolve franchise names to products, before anything is reconciled.

    A rename recomputes the id, because the id is derived from the title and nothing
    else. The spelling the source used stays as an alias: "King of Fighters" is what
    somebody will type even once the record says The King of Fighters XV. Where the
    canonical title is already its own entry the two now share an id, and the
    reconciliation that follows folds them like any other pair.
    """
    unknown = sorted(set(rules) - {g["id"] for g in games})
    if unknown:
        raise KeyError(f"{CANONICAL.name} names id(s) the source does not have: {unknown}")

    resolved = []
    for game in games:
        rule = rules.get(game["id"])
        if rule is None:
            resolved.append(game)
            continue
        if rule["action"] == "drop":
            continue
        was = game["name"]
        game["name"] = rule["value"]
        game["id"] = slugify(rule["value"])
        if was != game["name"] and was not in game["aliases"]:
            game["aliases"].append(was)
        resolved.append(game)
    return resolved


def read_catalog(path: Path) -> dict[str, dict]:
    """Genre, year and publisher, keyed by game id.

    ``year`` is the year the game came out -- the product a row names, in its
    earliest form, rather than a PS5-specific date, which most of this list does not
    have. ``scripts/fetch_years.py`` is where the bulk of it comes from.
    """
    rows: dict[str, dict] = {}
    for row in read_rows(path):
        game_id = (row.get("id") or "").strip()
        if not game_id:
            continue
        if game_id in rows:
            raise ValueError(f"{path.name} lists {game_id} twice")

        genre = (row.get("genre") or "").strip()
        year = (row.get("year") or "").strip()
        publisher = (row.get("publisher") or "").strip()
        if genre and genre not in GENRES:
            raise ValueError(f"{path.name}: {game_id} has genre {genre!r}, not one of {sorted(GENRES)}")

        rows[game_id] = {
            "genre": genre or None,
            "year": int(year) if year else None,
            "publisher": publisher or None,
        }
    return rows


def read_covers(path: Path) -> dict[str, dict]:
    """Packshot path and provenance, keyed by game id.

    A file without a source is refused. An image whose origin nobody wrote down is
    one nobody can re-fetch, re-license or replace, and a cover grid is the part of
    this repository most likely to be asked where it got something.
    """
    rows: dict[str, dict] = {}
    for row in read_rows(path):
        game_id = (row.get("id") or "").strip()
        if not game_id:
            continue
        file = (row.get("file") or "").strip()
        file2x = (row.get("file2x") or "").strip()
        source = (row.get("source") or "").strip()
        if file and not source:
            raise ValueError(f"{path.name}: {game_id} has a cover with no source")
        if source and not file:
            raise ValueError(f"{path.name}: {game_id} has a source with no cover")
        if file2x and not file:
            raise ValueError(f"{path.name}: {game_id} has a 2x cover with no 1x")
        rows[game_id] = {
            "cover": file or None,
            "cover_2x": file2x or None,
            "cover_source": source or None,
        }
    return rows


def read_coop(path: Path) -> dict[str, dict]:
    """The curated couch-coop worksheet, keyed by game id.

    A blank field is "not yet established" and stays None all the way to the JSON.
    It is never defaulted to zero or to "shared": the question this catalog exists
    to answer is how many people can play, and a fabricated answer is worse than an
    honest gap, which CL21's validator can still refuse.
    """
    rows: dict[str, dict] = {}
    for row in read_rows(path):
        game_id = (row.get("id") or "").strip()
        if not game_id:
            continue
        if game_id in rows:
            raise ValueError(f"{path.name} lists {game_id} twice")

        players = (row.get("max_players") or "").strip()
        screen = (row.get("screen") or "").strip()
        scope = (row.get("scope") or "").strip()
        if screen and screen not in SCREENS:
            raise ValueError(f"{path.name}: {game_id} has screen {screen!r}, not one of {sorted(SCREENS)}")
        if scope and scope not in SCOPES:
            raise ValueError(f"{path.name}: {game_id} has scope {scope!r}, not one of {sorted(SCOPES)}")

        rows[game_id] = {
            "max_players": int(players) if players else None,
            "screen": screen or None,
            "scope": scope or None,
        }
    return rows


def parse_line(raw: str) -> dict:
    """One source line to one record, splitting off a trailing parenthetical."""
    source = raw.strip()
    name = source
    note = None

    match = TRAILING_PAREN.search(name)
    if match:
        note = match.group(1).strip() or None
        name = name[: match.start()].strip()

    record = {"id": slugify(name), "name": name, "aliases": [], "source": source}
    record.update({"max_players": None, "screen": None, "scope": None})
    record.update({"genre": None, "year": None, "publisher": None})
    record.update({"cover": None, "cover_2x": None, "cover_source": None})
    record["source_note"] = note
    return record


def fold(survivor: dict, folded: dict) -> None:
    """Absorb one record into another, keeping every name it was known by.

    A caveat is adopted only where the survivor has none: the source attaches
    "(modo Zombies)" to one spelling of a title and not the other, and dropping it
    on the merge would lose the fact that decides the purchase.
    """
    for name in [folded["name"], *folded["aliases"]]:
        if name != survivor["name"] and name not in survivor["aliases"]:
            survivor["aliases"].append(name)
    if survivor["source_note"] is None:
        survivor["source_note"] = folded["source_note"]


def reconcile(games: list[dict]) -> list[dict]:
    """One entry per product: collapse repeated ids, then apply MERGES."""
    collapsed: dict[str, dict] = {}
    for game in games:
        existing = collapsed.get(game["id"])
        if existing is None:
            collapsed[game["id"]] = game
        else:
            fold(existing, game)

    for survivor_id, folded_ids in MERGES.items():
        if survivor_id not in collapsed:
            raise KeyError(f"MERGES names a survivor the source does not have: {survivor_id}")
        for folded_id in folded_ids:
            folded = collapsed.pop(folded_id, None)
            if folded is None:
                raise KeyError(f"MERGES names an entry the source does not have: {folded_id}")
            fold(collapsed[survivor_id], folded)

    for game in collapsed.values():
        game["aliases"].sort()
    return list(collapsed.values())


def read_entries(text: str) -> list[str]:
    """Every non-comment, non-blank line, in the order the source lists them."""
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def build(text: str) -> dict:
    parsed = [parse_line(entry) for entry in read_entries(text)]
    games = reconcile(apply_canonical(parsed, read_canonical(CANONICAL)))

    ids = {g["id"] for g in games}
    for path, reader in ((COOP, read_coop), (CATALOG, read_catalog), (COVERS, read_covers)):
        rows = reader(path)
        unknown = sorted(set(rows) - ids)
        if unknown:
            raise KeyError(f"{path.name} names id(s) the dataset does not have: {unknown}")
        for game in games:
            game.update(rows.get(game["id"], {}))

    # Every record ends up with a cover: a packshot where one exists, and otherwise
    # the generated card, so the grid never has a hole to lay out around.
    for game in games:
        if game["cover"] is None:
            game["cover"] = GENERATED_COVER.format(id=game["id"])
            game["cover_source"] = "generated"

    return {
        "schema_version": SCHEMA_VERSION,
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "count": len(games),
        "games": games,
    }


def main() -> int:
    if not SOURCE.exists():
        print(f"build-dataset: missing {SOURCE}", file=sys.stderr)
        return 1

    dataset = build(SOURCE.read_text(encoding="utf-8"))
    TARGET.write_text(
        json.dumps(dataset, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    entries = len(read_entries(SOURCE.read_text(encoding="utf-8")))
    merged = [g for g in dataset["games"] if g["aliases"]]
    print(
        f"build-dataset: {entries} source line(s) -> {dataset['count']} record(s) -> "
        f"{TARGET.relative_to(ROOT).as_posix()}",
        file=sys.stderr,
    )
    # Three different things remove or rewrite a line, and lumping them together
    # hides which one moved: a drop deletes a record, a fold merges two, a rename
    # leaves the count alone and only changes what the record is called.
    rules = read_canonical(CANONICAL)
    dropped = sum(1 for r in rules.values() if r["action"] == "drop")
    print(
        f"build-dataset: {dropped} dropped, "
        f"{entries - dropped - dataset['count']} folded, "
        f"{sum(1 for r in rules.values() if r['action'] == 'rename')} renamed",
        file=sys.stderr,
    )
    for game in sorted(merged, key=lambda g: g["id"]):
        print(f"  {game['id']} <- {', '.join(game['aliases'])}", file=sys.stderr)

    # Coverage is reported every run: the gap is the work, and a silent gap is a lie.
    known = [g for g in dataset["games"] if g["max_players"] is not None]
    print(
        f"build-dataset: couch-coop known for {len(known)}/{dataset['count']}, "
        f"{dataset['count'] - len(known)} still blank",
        file=sys.stderr,
    )

    genred = [g for g in dataset["games"] if g["genre"] is not None]
    print(
        f"build-dataset: genre known for {len(genred)}/{dataset['count']}, "
        f"{dataset['count'] - len(genred)} still blank",
        file=sys.stderr,
    )

    dated = [g for g in dataset["games"] if g["year"] is not None]
    print(
        f"build-dataset: year known for {len(dated)}/{dataset['count']}, "
        f"{dataset['count'] - len(dated)} still blank",
        file=sys.stderr,
    )

    # An id is the record's identity from here on; two of them is a bug, not a duplicate.
    clashes = [i for i, n in Counter(g["id"] for g in dataset["games"]).items() if n > 1]
    if clashes:
        print(f"build-dataset: ERROR repeated id(s): {clashes}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
