#!/usr/bin/env python3
"""Fetch a real packshot for every game a store search can confidently identify.

Why Steam, in a PlayStation catalogue
-------------------------------------
CL6 asks for covers in 2:3 portrait, served from this repository, and records the
blocker: a source still had to be chosen. The PlayStation Store is the obvious one
and does not work. It renders search results client-side, behind a GraphQL
persisted-query hash that changes with every front-end deploy, so nothing here can
turn a title into a packshot without driving a browser -- a dependency this
repository has spent CL7 avoiding.

Steam publishes a keyless search endpoint and a portrait "library capsule" at
exactly 600x900, which is the 2:3 the design asks for, with a 1200x1800 twin that
fills the second density CL18 wants. It is the PC key art rather than the PSN
packshot, and for most of this list it is the same publisher artwork. Where it is
not, the row still says where the image came from, which is the whole reason the
source column is mandatory.

Why a wrong cover is worse than a blank one
-------------------------------------------
The README's rule for a blank worksheet field is that nothing invents a value,
because a wrong one sends somebody to buy the wrong game. A cover is the loudest
field there is: it is what a reader recognises before they read the title. So the
match here is deliberately narrow -- the store's name has to equal the catalogue's
name once typography is stripped, or the id has to appear in ALIASES below with a
reason. Everything else stays blank and keeps its generated card, and the run
prints what it refused so the gap is visible rather than quietly filled.

Two of the guesses that went into ALIASES were wrong on the first attempt: an
appid typed from memory resolved to an unrelated demo, and another to a DLC for a
different game. That is why every candidate is confirmed against appdetails and
rejected unless the store calls it a game -- the capsule CDN will happily serve
art for an appid whose store page does not exist.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterator
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DATASET = ROOT / "data" / "games.json"
COVERS_CSV = ROOT / "data" / "covers.csv"
COVERS_DIR = ROOT / "assets" / "covers"

SEARCH = "https://store.steampowered.com/api/storesearch/?term={}&cc=us&l=en"
DETAILS = "https://store.steampowered.com/api/appdetails?appids={}&l=en"
CAPSULE = "https://cdn.cloudflare.steamstatic.com/steam/apps/{}/library_600x900{}.jpg"
STORE_PAGE = "https://store.steampowered.com/app/{}/"

# Steam blocks the default urllib agent outright.
AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

# The endpoint is undocumented and unmetered; this is slow enough to stay welcome.
PAUSE = 0.45

# Steam's own pair, and not a pixel invented on top of it. The "600x900" in the
# capsule's filename is the CSS size, not the file's: library_600x900.jpg is
# 300x450 and the _2x twin is the 600x900. So 600x900 is the ceiling this source
# has, and shipping a 400x600 "1x" would buy a sharper grid card by forfeiting any
# truthful 2x -- a 600x900 behind a 2x descriptor would be 1.5x and the browser
# would size against it as though it were double.
#
# The cost is the detail dialog, which is 380 CSS px wide and so upscales 300x450
# by a quarter on a 1x screen. The grid, which is the page, is 120-200 px a card
# and exact at both densities.
ONE_X = (300, 450)
TWO_X = (600, 900)

# 1x carries the visible artefacts, so it gets the higher number. At 2x every
# pixel is half a device pixel and 78 is indistinguishable from 90 at three times
# the bytes.
QUALITY_1X = 82
QUALITY_2X = 78

# A capsule that is not 2:3 is not the asset this expects, and cropping one to fit
# would cut somebody's key art in half. One percent absorbs Steam's odd 599x900.
RATIO_TOLERANCE = 0.01

# Where the console title and the Steam title are genuinely different names for
# the same thing. Each of these was read off a search result or appdetails, never
# typed from memory, and each is confirmed to be type "game" at run time.
ALIASES = {
    # Steam ships the remaster under the plain name; the console SKU adds the word.
    "castle-crashers-remastered": 204360,
    # The console release of Original Sin is the Enhanced Edition.
    "divinity-original-sin": 373420,
    # Renamed "Dive Harder Edition" on Steam after the update of the same name.
    "helldivers": 394510,
    # "Couch Edition" is the console SKU of the same game.
    "out-of-space-couch-edition": 400080,
    # The base app was renamed when the Sunset Edition update shipped.
    "sea-of-stars": 1244090,
    # Champion Edition is the console SKU; Steam sells the base game and sells the
    # Champion upgrade separately, so no listing carries the console's name.
    "street-fighter-v-champion-edition": 310950,
    # Plus is the console SKU; Steam sells the base game and the expansion apart.
    "sonic-origins-plus": 1794960,
    # The PS5 SKU of Tetris Effect is Connected.
    "tetris-effect": 1003590,
    # The base app was renamed Final Cut.
    "the-last-oricru": 1663640,
    # The catalogue abbreviates what Steam spells out.
    "tmnt-the-cowabunga-collection": 1659600,
    # Slayer Edition is the console edition of Chaosbane.
    "warhammer-chaosbane-slayer-edition": 774241,
    # Steam appends the licence's full name to both WRC titles.
    "wrc-10": 1462810,
    "wrc-generations": 1953520,
    # Search returns nothing for this one, though the store page is public.
    "wwe-2k23": 1942660,
}

# Titles a strict match still gets wrong, because the name is generic enough to
# collide with an unrelated product. Listed rather than silently allowed, so the
# refusal is reviewable.
REJECT = {
    # The couch list means Housemarque's PS4 shooter, not "Marsmare: Alienation".
    "alienation",
    # Battle.net only; Steam sells Diablo IV and has never sold III.
    "diablo-iii",
    # Steam's "Omega Strikers" is a different game by a different studio.
    "omega-strike",
    # R Online was a delisted battle-royale spin-off, not Super Bomberman R.
    "super-bomberman-r-online",
}

TRADEMARKS = "™®©"


def normalise(name: str) -> str:
    """A title reduced to the letters and digits that identify it.

    The trademark marks come off before NFKD rather than after, because NFKD
    expands U+2122 to the letters "TM" -- which silently turned "Gauntlet(tm)
    Slayer Edition" into "gauntlettm slayer edition" and lost thirteen matches
    that were sitting right there in the search results.
    """
    name = name.translate({ord(c): None for c in TRADEMARKS})
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c)).lower()
    # Spelled out, so "Blood & Teef" and "Blood and Teef" are the same title and
    # "1 + 2" cannot collapse into "12".
    name = name.replace("&", " and ").replace("+", " plus ")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", name).split())


def queries(name: str) -> list[str]:
    """The search terms to try for one title, most faithful first.

    The endpoint returns nothing at all for a term carrying an em dash or a
    trademark mark, so the punctuation-free form is not a fallback for obscure
    titles -- it is what finds Tony Hawk's Pro Skater and Scott Pilgrim.
    """
    bare = " ".join(re.sub(r"[^A-Za-z0-9' ]+", " ", name).split())
    # Literal single spaces around the separator rather than \s+, which is enough
    # for every title on this list and keeps "Spider-Man" in one piece.
    stem = re.split(r" [-–—] |: ", name)[0]
    head = " ".join(re.sub(r"[^A-Za-z0-9' ]+", " ", stem).split())
    out: list[str] = []
    for term in (name, bare, head):
        if term and term.lower() not in {o.lower() for o in out}:
            out.append(term)
    return out


class Absent(Exception):
    """The server answered, and the answer was that there is nothing there."""


def once(url: str, binary: bool):
    """A single GET. Raises Absent for a 403 or 404, which is not worth a retry."""
    request = urllib.request.Request(url, headers={"User-Agent": AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read()
    except urllib.error.HTTPError as exc:
        # A missing capsule is an answer, not a failure to retry.
        if exc.code in (403, 404):
            raise Absent from exc
        raise
    return payload if binary else json.loads(payload.decode("utf-8"))


def fetch(url: str, binary: bool = False):
    """One GET with backoff, returning None where the answer is "not there"."""
    retry = (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, json.JSONDecodeError)
    for attempt in range(4):
        try:
            return once(url, binary)
        except Absent:
            return None
        except retry:
            if attempt == 3:
                raise
            time.sleep(2 * (attempt + 1))
    return None


def confirm(appid: int) -> str | None:
    """The store's own name for an appid, or None if it is not a game.

    The capsule CDN serves art for appids whose store page does not exist, so the
    image arriving is no evidence that the appid is the product wanted. This is
    the check that catches an alias pointing at a demo or a DLC.
    """
    payload = fetch(DETAILS.format(appid))
    entry = (payload or {}).get(str(appid)) or {}
    if not entry.get("success"):
        return None
    data = entry.get("data") or {}
    return data.get("name") if data.get("type") == "game" else None


def candidates(name: str) -> Iterator[int]:
    """Appids a search turns up whose name already matches, laziest first.

    A generator rather than a list so the caller stops the moment one confirms:
    almost every title matches on the first of the three query forms, and
    resolving the other two would treble a run of 184 for nothing. Only
    name-matching results are yielded, because confirm() costs a request each.
    """
    target = normalise(name)
    seen: set[int] = set()
    for term in queries(name):
        payload = fetch(SEARCH.format(urllib.parse.quote(term)))
        time.sleep(PAUSE)
        for item in (payload or {}).get("items") or []:
            appid = item.get("id")
            if item.get("type") != "app" or appid in seen:
                continue
            seen.add(appid)
            if normalise(item.get("name") or "") == target:
                yield appid


def resolve(game: dict) -> tuple[int | None, str, str]:
    """Find the appid for one game. Returns (appid, store name, how)."""
    game_id, name = game["id"], game["name"]

    if game_id in REJECT:
        return None, "", "refused"

    if game_id in ALIASES:
        store_name = confirm(ALIASES[game_id])
        if not store_name:
            return None, "", "alias is not a game"
        return ALIASES[game_id], store_name, "alias"

    target = normalise(name)
    for appid in candidates(name):
        store_name = confirm(appid)
        time.sleep(PAUSE)
        # Checked again against appdetails, because the search index and the store
        # disagree often enough: a result can be named for the game and resolve to
        # its demo.
        if store_name and normalise(store_name) == target:
            return appid, store_name, "search"
    return None, "", "no confident match"


def capsule(appid: int) -> Image.Image | None:
    """The portrait capsule at the best size Steam has, or None."""
    for suffix in ("_2x", ""):
        payload = fetch(CAPSULE.format(appid, suffix), binary=True)
        if not payload:
            continue
        image = Image.open(io.BytesIO(payload))
        image.load()
        ratio = image.width / image.height
        if abs(ratio - 2 / 3) > RATIO_TOLERANCE:
            print(
                f"  capsule{suffix} is {image.width}x{image.height}, not 2:3 -- skipped",
                file=sys.stderr,
            )
            continue
        return image.convert("RGB")
    return None


def write_images(game_id: str, image: Image.Image) -> tuple[str, str]:
    """Write the 1x and 2x WebP, returning their repository-relative paths.

    The 2x is only written where the source can fill it. Upscaling 600x900 into
    800x1200 would put a larger file behind a 2x descriptor without adding a
    single pixel of detail, which is worse than having no 2x at all.
    """
    COVERS_DIR.mkdir(parents=True, exist_ok=True)

    one = image.resize(ONE_X, Image.LANCZOS)
    one_path = COVERS_DIR / f"{game_id}.webp"
    one.save(one_path, "WEBP", quality=QUALITY_1X, method=6)

    two_rel = ""
    if image.width >= TWO_X[0] and image.height >= TWO_X[1]:
        two = image.resize(TWO_X, Image.LANCZOS)
        two_path = COVERS_DIR / f"{game_id}@2x.webp"
        two.save(two_path, "WEBP", quality=QUALITY_2X, method=6)
        two_rel = two_path.relative_to(ROOT).as_posix()

    return one_path.relative_to(ROOT).as_posix(), two_rel


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


def existing(path: Path) -> dict[str, dict[str, str]]:
    """The worksheet as it stands, so a filled row is never overwritten."""
    text = "\n".join(
        line for line in path.read_text(encoding="utf-8").splitlines()
        if not line.startswith("#")
    )
    return {
        (row.get("id") or "").strip(): row
        for row in csv.DictReader(io.StringIO(text))
        if (row.get("id") or "").strip()
    }


def write_worksheet(rows: dict[str, dict[str, str]]) -> None:
    """Rewrite covers.csv, comment block first, one row per id in id order."""
    out = io.StringIO()
    writer = csv.DictWriter(
        out, fieldnames=["id", "file", "file2x", "source"], lineterminator="\n"
    )
    writer.writeheader()
    for game_id in sorted(rows):
        row = rows[game_id]
        writer.writerow({
            "id": game_id,
            "file": (row.get("file") or "").strip(),
            "file2x": (row.get("file2x") or "").strip(),
            "source": (row.get("source") or "").strip(),
        })
    COVERS_CSV.write_text(
        "\n".join(header(COVERS_CSV)) + "\n" + out.getvalue(), encoding="utf-8"
    )


def acquire(game: dict, dry_run: bool) -> tuple[dict[str, str] | None, str]:
    """Resolve one game and fetch its art. Returns (row, note).

    A row of None is a game left to its generated card, and the note says which
    step declined it -- the report prints those verbatim, because an unexplained
    blank is the thing this script exists not to produce.
    """
    appid, store_name, how = resolve(game)
    if not appid:
        return None, how

    if dry_run:
        return {}, f"{how} -> {appid} {store_name}"

    image = capsule(appid)
    if image is None:
        return None, "no portrait capsule"

    one, two = write_images(game["id"], image)
    row = {
        "id": game["id"],
        "file": one,
        "file2x": two,
        "source": STORE_PAGE.format(appid),
    }
    return row, f"{how} -> {appid} {store_name}"


def select(games: list[dict], only: list[str] | None) -> list[dict]:
    """The games to work on, warning about an id that is not in the dataset."""
    if not only:
        return games
    wanted = set(only)
    chosen = [g for g in games if g["id"] in wanted]
    for game_id in sorted(wanted - {g["id"] for g in chosen}):
        print(f"fetch-covers: no game with id {game_id}", file=sys.stderr)
    return chosen


def run(
    games: list[dict], rows: dict[str, dict[str, str]], dry_run: bool, force: bool
) -> tuple[int, int, list[tuple[str, str]]]:
    """Work the list, filling rows in place. Returns (filled, skipped, refused)."""
    filled, skipped = 0, 0
    refused: list[tuple[str, str]] = []

    for index, game in enumerate(games, 1):
        current = rows.get(game["id"]) or {}
        if (current.get("file") or "").strip() and not force:
            skipped += 1
            continue

        row, note = acquire(game, dry_run)
        where = f"{index:3}/{len(games)}"
        if row is None:
            refused.append((game["name"], note))
            print(f"{where} ---- {game['name']}  ({note})", file=sys.stderr)
            continue

        if row:
            rows[game["id"]] = row
        filled += 1
        print(f"{where} ok   {game['name']}  {note}", file=sys.stderr)

    return filled, skipped, refused


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--dry-run", action="store_true",
        help="resolve and report, without downloading or writing anything",
    )
    parser.add_argument(
        "--only", metavar="ID", action="append",
        help="just this game id, repeatable -- for checking one stubborn title",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="re-fetch a game whose row is already filled",
    )
    args = parser.parse_args()

    if not DATASET.exists():
        print("fetch-covers: run build_dataset.py first", file=sys.stderr)
        return 1

    games = select(json.loads(DATASET.read_text(encoding="utf-8"))["games"], args.only)
    if not games:
        return 1

    rows = existing(COVERS_CSV)
    filled, skipped, refused = run(games, rows, args.dry_run, args.force)

    if not args.dry_run:
        write_worksheet(rows)

    print(
        f"\nfetch-covers: {filled} packshot(s), {len(refused)} left to the generated "
        f"card, {skipped} already filled",
        file=sys.stderr,
    )
    if refused:
        print("fetch-covers: no packshot for --", file=sys.stderr)
        for name, why in refused:
            print(f"  {name}  ({why})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
