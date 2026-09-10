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

* Duplicates survive it (CL2). Four lines repeat verbatim, and a couple more name
  the same game twice in different words. Collapsing them here would hide the very
  entries CL2 has to reconcile, so identical ids are emitted and merely counted.
* Collection names survive it (CL5). "Trine Series" and "Bleed 1 e 2" name a set
  rather than a product, and picking the canonical title is a judgement about the
  PSN catalog that this script has no way to make.
* ``players``, ``coop``, ``genre``, ``year``, ``publisher`` and ``cover`` are
  emitted as null (CL3, CL4, CL6). The schema carries them from the first commit
  so the readers can be written against a stable shape, but a value invented here
  would be a guess wearing the costume of data.

What the source puts in parentheses is kept verbatim in ``source_note`` -- the
"(modo Zombies)" and "(Tela dividida)" caveats are what CL11 surfaces, and they
would be lost if the title were simply cleaned.
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "data" / "source-list.txt"
TARGET = ROOT / "data" / "games.json"

SCHEMA_VERSION = 1

# Filled by later tasks; declared here so every reader sees one record shape.
DEFERRED_FIELDS = ("players", "coop", "genre", "year", "publisher", "cover")

# A trailing "(...)" is the source's caveat about the entry, not part of its title.
TRAILING_PAREN = re.compile(r"\s*\(([^()]*)\)\s*$")


def slugify(name: str) -> str:
    """A stable, url-safe id derived from the title alone.

    Derived rather than assigned so that re-running this script never renumbers a
    record: the id of a line is a function of its text and nothing else.
    """
    decomposed = unicodedata.normalize("NFKD", name)
    ascii_only = "".join(c for c in decomposed if not unicodedata.combining(c))
    lowered = ascii_only.lower().replace("'", "").replace("’", "")
    return re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9]+", "-", lowered)).strip("-")


def parse_line(raw: str) -> dict:
    """One source line to one record, splitting off a trailing parenthetical."""
    source = raw.strip()
    name = source
    note = None

    match = TRAILING_PAREN.search(name)
    if match:
        note = match.group(1).strip() or None
        name = name[: match.start()].strip()

    record = {"id": slugify(name), "name": name, "source": source}
    record.update({field: None for field in DEFERRED_FIELDS})
    record["source_note"] = note
    return record


def read_entries(text: str) -> list[str]:
    """Every non-comment, non-blank line, in the order the source lists them."""
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def build(text: str) -> dict:
    games = [parse_line(entry) for entry in read_entries(text)]
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

    repeated = sorted(
        item for item, n in Counter(g["id"] for g in dataset["games"]).items() if n > 1
    )
    print(
        f"build-dataset: {dataset['count']} record(s) -> "
        f"{TARGET.relative_to(ROOT).as_posix()}",
        file=sys.stderr,
    )
    # Reported and not resolved: this is the list CL2 reconciles.
    print(f"build-dataset: {len(repeated)} repeated id(s) left for CL2", file=sys.stderr)
    for item in repeated:
        print(f"  {item}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
