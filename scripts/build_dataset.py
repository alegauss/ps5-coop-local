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

* Collection names survive it (CL5). "Trine Series" and "Bleed 1 e 2" name a set
  rather than a product, and picking the canonical title is a judgement about the
  PSN catalog that this script has no way to make.
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

Two gaps are deliberate. ``year`` is blank throughout -- the axis wanted is the PS5
release year, and most of this list is PS4 software played through back-compat,
which has no PS5 release date to carry; the column stays so the answer has somewhere
to land. And a handful of titles have no genre because the ten labels have no honest
home for them: "A Way Out" is a co-op cinematic adventure, and calling it a
platformer to avoid a blank would put it under a filter nobody would find it in.
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
TARGET = ROOT / "data" / "games.json"

SCHEMA_VERSION = 1

# Filled by later tasks; declared here so every reader sees one record shape.
DEFERRED_FIELDS = ("cover",)

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


def read_catalog(path: Path) -> dict[str, dict]:
    """Genre, year and publisher, keyed by game id.

    ``year`` is the PS5 release year and is blank throughout for now: most of this
    list is PS4 software played through back-compat, which has no PS5 release date
    to carry. The column stays so the answer has somewhere to land.
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
    record.update({field: None for field in DEFERRED_FIELDS})
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
    games = reconcile([parse_line(entry) for entry in read_entries(text)])

    ids = {g["id"] for g in games}
    for path, reader in ((COOP, read_coop), (CATALOG, read_catalog)):
        rows = reader(path)
        unknown = sorted(set(rows) - ids)
        if unknown:
            raise KeyError(f"{path.name} names id(s) the dataset does not have: {unknown}")
        for game in games:
            game.update(rows.get(game["id"], {}))

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
    # An exact repeat contributes no alias, so the two are counted apart.
    aliased = sum(len(g["aliases"]) for g in merged)
    print(
        f"build-dataset: {entries - dataset['count']} line(s) folded -- "
        f"{entries - dataset['count'] - aliased} exact repeat(s), "
        f"{aliased} under another name",
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

    # An id is the record's identity from here on; two of them is a bug, not a duplicate.
    clashes = [i for i, n in Counter(g["id"] for g in dataset["games"]).items() if n > 1]
    if clashes:
        print(f"build-dataset: ERROR repeated id(s): {clashes}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
