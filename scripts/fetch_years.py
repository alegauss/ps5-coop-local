#!/usr/bin/env python3
"""Fill the year column from the store pages data/covers.csv already records.

What the column means, and what it used to mean
-----------------------------------------------
CL4 asked for a year "to sort and give context", and defined it as the PS5 release
year. That definition is why the column sat blank on all 184 records: most of this
list is PS4 software played through back-compat, which has no PS5 release date to
carry, so the honest value was nothing -- for the whole catalogue, permanently.

A column that is null on every record is worse than one that does not exist. The
site does not merely tolerate it: index.html ships a "Newest first" option and the
detail panel ships a "Released" row, both of which CL10 wired to a field nothing
ever filled. So the column is wanted; it was the definition that could not be met.

It now means **the year this product first released, on any platform**. That is the
"how old is this game" axis the sort control implies, it is the same number for all
but a handful of titles, and unlike the old definition it can actually be sourced.

Where the number comes from
---------------------------
Nowhere new. data/covers.csv already records the Steam store page each packshot came
from, because CL6 made a cover without a source a refusal. That page states a release
date, so the provenance for the year is the provenance already in the repository --
this script resolves no titles and searches for nothing, which is the whole reason it
is separate from fetch_covers.py rather than part of it.

The date Steam states is the date **its own listing** released, which is a different
fact and agrees with this column only when the launch was simultaneous. It usually
was. Where it was not, there are two cases and they are not the same mistake:

* Steam listed the game years late, because it launched on console, Origin, Epic or
  Battle.net first. A Way Out is a 2018 game whose Steam page says 2020, Returnal a
  2021 PS5 exclusive whose page says 2023. ``LATE`` corrects those, one reason each.
* The recorded page is a **different product** from the entry. Champion Edition is
  2020 and the page is the 2016 base game; Plus is 2023 and the page is Origins.
  ``LATE`` corrects the ones whose real year is established, and ``REJECT`` refuses
  the rest -- and each of those is also a wrong cover, since CL6 read the same page.

Both lists are read off a store listing or a release announcement, never typed from
memory, and both carry the reason inline: an override with no reason beside it is
indistinguishable from a guess six months later.

The rest stay blank, and the run prints how many. A year nobody sourced is not
invented here for the same reason a player count is not: the README's rule for a
blank worksheet field is that nothing fills it with a guess.

Like fetch_covers.py this goes to the network, so it is not part of the build loop
and CI never runs it. A row that already carries a year is left alone unless --force.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COVERS_CSV = ROOT / "data" / "covers.csv"
CATALOG_CSV = ROOT / "data" / "catalog.csv"

DETAILS = "https://store.steampowered.com/api/appdetails?appids={}&filters=release_date&l=en"

# Steam blocks the default urllib agent outright.
AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

# appdetails is undocumented and rate-limited to roughly one call a second before it
# starts answering with nothing at all. Slow enough to stay welcome, and a run of
# 148 still finishes inside three minutes.
PAUSE = 1.1

# The appid out of a recorded store page, which is the only field this reads from
# covers.csv: a source column pointing anywhere else is not a Steam page and is skipped.
APPID = re.compile(r"store\.steampowered\.com/app/(\d+)")

# Steam writes the date a dozen ways -- "24 Sep, 2026", "Sep 24, 2026", "2026", "Q3
# 2026" -- and the year is the only part this column holds, so a bare four digits in
# the range a video game can have released in is all that has to be recognised.
YEAR = re.compile(r"\b(19[7-9]\d|20[0-4]\d)\b")

# Where the recorded Steam page states a year that is not this product's, with the
# year that is and why the page disagrees. Two shapes, both listed here because the
# fix is the same: Steam got the listing late, or the page is a neighbouring SKU.
LATE = {
    # Launched on console, Origin, Epic or Battle.net first, and reached Steam later.
    "a-way-out": (2018, "PS4, Xbox and Origin in March 2018; Steam only in 2020"),
    "borderlands-3": (2019, "console and Epic in September 2019; Steam a year later"),
    "call-of-duty-black-ops-cold-war": (2020, "November 2020; Steam only in 2023"),
    "minecraft-dungeons": (2020, "May 2020; Steam in 2021"),
    "overcooked-all-you-can-eat": (2020, "PS5 launch window, November 2020; Steam in 2021"),
    "puyo-puyo-tetris-2": (2020, "December 2020 on console; Steam in 2021"),
    "returnal": (2021, "PS5 exclusive, April 2021; Steam in 2023"),
    "sackboy-a-big-adventure": (2020, "PS5 launch title, November 2020; Steam in 2022"),
    "salt-and-sacrifice": (2022, "May 2022 on PlayStation and Epic; Steam in 2023"),
    "the-king-of-fighters-xv": (2022, "February 2022; the recorded listing is a later SKU"),
    "tony-hawks-pro-skater-1-2": (2020, "September 2020 on console; Steam in 2023"),
    "unravel-two": (2018, "June 2018 on console and Origin; Steam in 2020"),
    # The recorded page is a neighbouring SKU whose year is not this entry's.
    "quake": (2021, "the PlayStation product is the 2021 Enhanced release"),
    "scott-pilgrim-vs-the-world-the-game-complete-edition": (
        2021, "the Complete Edition is January 2021; the page's date is Steam's, 2023",
    ),
    "sonic-origins-plus": (2023, "Plus is the 2023 edition; the page is Origins, 2022"),
    "street-fighter-v-champion-edition": (
        2020, "Champion Edition is February 2020; the page is the 2016 base game",
    ),
    "warhammer-chaosbane-slayer-edition": (
        2021, "the Slayer Edition is 2021; the page is Chaosbane, 2019",
    ),
    "castle-crashers-remastered": (
        2015, "the Remastered SKU is September 2015; the page is the 2012 original",
    ),
}

# Pages whose date says nothing about this entry, and where nothing checked here
# establishes the right year either. Left blank rather than guessed. Each of these is
# a wrong cover as well as a missing year, because CL6 read the same page -- which is
# CL5's to fix, since in every case the entry's own name is what pointed here.
# Empty, and kept rather than deleted: both entries it held were resolved by CL4 once
# somebody went looking -- Castle Crashers Remastered moved to LATE with its real year,
# and Samurai Gunn 2 turned out to have shipped alongside its Early Access listing. The
# mechanism stays because the next wrong page will need it, and a blank list says
# plainly that nothing is currently refused rather than that nothing ever was.
REJECT: dict[str, str] = {}


def fetch(url: str):
    """One GET with backoff. None where the server says there is nothing there."""
    request = urllib.request.Request(url, headers={"User-Agent": AGENT})
    retry = (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code in (403, 404):
                return None
            if attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))
        except retry:
            if attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))
    return None


def released(appid: str) -> tuple[int | None, str]:
    """The release year Steam states for one appid, and what it said.

    A title still marked "coming soon" is refused rather than recorded: the date on
    an unreleased product is a plan, and this column is meant to say how old a game
    is. Nothing on this list is unreleased, so the check is a guard and not a filter.
    """
    payload = fetch(DETAILS.format(appid))
    entry = (payload or {}).get(str(appid)) or {}
    if not entry.get("success"):
        return None, "appdetails has no such app"

    date = (entry.get("data") or {}).get("release_date") or {}
    said = (date.get("date") or "").strip()
    if date.get("coming_soon"):
        return None, f"coming soon ({said or 'no date'})"
    match = YEAR.search(said)
    if not match:
        return None, f"no year in {said!r}" if said else "no release date"
    return int(match.group(1)), said


def header(path: Path) -> list[str]:
    """The comment block at the top of a worksheet, kept verbatim.

    Those lines document the columns and are the only place the file explains
    itself. Rewriting the CSV with csv.writer alone would drop them.
    """
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("#"):
            break
        lines.append(line)
    return lines


def rows_of(path: Path) -> dict[str, dict[str, str]]:
    """A worksheet as it stands, keyed by id, with the commentary stripped."""
    text = "\n".join(
        line for line in path.read_text(encoding="utf-8").splitlines()
        if not line.startswith("#")
    )
    return {
        (row.get("id") or "").strip(): row
        for row in csv.DictReader(io.StringIO(text))
        if (row.get("id") or "").strip()
    }


def write_catalog(rows: dict[str, dict[str, str]]) -> None:
    """Rewrite catalog.csv, comment block first, one row per id in id order."""
    out = io.StringIO()
    fields = ["id", "genre", "year", "publisher"]
    writer = csv.DictWriter(out, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for game_id in sorted(rows):
        row = rows[game_id]
        writer.writerow({f: (row.get(f) or "").strip() for f in fields} | {"id": game_id})
    CATALOG_CSV.write_text(
        "\n".join(header(CATALOG_CSV)) + "\n" + out.getvalue(), encoding="utf-8"
    )


def appids(covers: dict[str, dict[str, str]], only: list[str] | None) -> list[tuple[str, str]]:
    """Every (id, appid) a recorded cover source yields, in id order."""
    wanted = set(only or ())
    found: list[tuple[str, str]] = []
    for game_id in sorted(covers):
        if wanted and game_id not in wanted:
            continue
        match = APPID.search((covers[game_id].get("source") or "").strip())
        if match:
            found.append((game_id, match.group(1)))
    for game_id in sorted(wanted - {g for g, _ in found}):
        print(f"fetch-years: no recorded Steam page for {game_id}", file=sys.stderr)
    return found


def run(
    pairs: list[tuple[str, str]], catalog: dict[str, dict[str, str]], force: bool
) -> tuple[int, int, int, list[tuple[str, str]]]:
    """Work the list, filling rows in place.

    Returns (fetched, corrected, skipped, refused). A LATE entry costs no request:
    its year is already established and the page's date is known to disagree, so
    asking would only spend a second to be told something this file does not believe.
    """
    fetched = corrected = skipped = 0
    refused: list[tuple[str, str]] = []

    for index, (game_id, appid) in enumerate(pairs, 1):
        where = f"{index:3}/{len(pairs)}"
        row = catalog.get(game_id)
        if row is None:
            refused.append((game_id, "not in catalog.csv"))
            continue
        if (row.get("year") or "").strip() and not force:
            skipped += 1
            continue

        if game_id in REJECT:
            refused.append((game_id, REJECT[game_id]))
            print(f"{where} ---- {game_id}  ({REJECT[game_id]})", file=sys.stderr)
            continue

        if game_id in LATE:
            year, why = LATE[game_id]
            row["year"] = str(year)
            corrected += 1
            print(f"{where} late {game_id}  {year}  ({why})", file=sys.stderr)
            continue

        year, said = released(appid)
        time.sleep(PAUSE)
        if year is None:
            refused.append((game_id, said))
            print(f"{where} ---- {game_id}  ({said})", file=sys.stderr)
            continue

        row["year"] = str(year)
        fetched += 1
        print(f"{where} ok   {game_id}  {year}  ({said})", file=sys.stderr)

    return fetched, corrected, skipped, refused


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--dry-run", action="store_true",
        help="fetch and report, without writing the worksheet",
    )
    parser.add_argument(
        "--only", metavar="ID", action="append",
        help="just this game id, repeatable -- for checking one stubborn title",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="re-fetch a game whose year is already filled",
    )
    args = parser.parse_args()

    catalog = rows_of(CATALOG_CSV)
    pairs = appids(rows_of(COVERS_CSV), args.only)
    if not pairs:
        print("fetch-years: no Steam pages recorded in covers.csv", file=sys.stderr)
        return 1

    fetched, corrected, skipped, refused = run(pairs, catalog, args.force)

    if not args.dry_run:
        write_catalog(catalog)

    blank = sum(1 for r in catalog.values() if not (r.get("year") or "").strip())
    print(
        f"\nfetch-years: {fetched} year(s) from a recorded store page, {corrected} "
        f"corrected against it, {skipped} already filled, {len(refused)} refused -- "
        f"{blank} of {len(catalog)} still blank",
        file=sys.stderr,
    )
    if refused:
        print("fetch-years: no year for --", file=sys.stderr)
        for game_id, why in refused:
            print(f"  {game_id}  ({why})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
