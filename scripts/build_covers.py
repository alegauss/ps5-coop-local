#!/usr/bin/env python3
"""Generate the fallback cover card for every game that has no packshot.

Why these are not WebP
----------------------
The design asks for covers in 2:3 portrait, served locally, as WebP -- and that
still holds for real packshots, which are photographs and compress like one. This
script generates the *other* half: the typographic card shown where no art exists.
That card is two glyphs and a rectangle, so SVG is both smaller (under a kilobyte
against several for a rasterised card) and sharp at any grid size, where a WebP
would have to pick a resolution and be wrong at half of them. It also needs no
image toolchain, which means the cards regenerate anywhere the dataset does.

A card is deliberately not a gray rectangle. It carries the initials and the
genre's colour, so a grid of them still reads as a shelf and still tells the
player something, and every card is the same 2:3 box so nothing shifts when real
art lands beside it.
"""

from __future__ import annotations

import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
COVERS = ROOT / "assets" / "covers"

# 2:3, the PS5 packshot ratio. Everything below is in these units.
WIDTH, HEIGHT = 200, 300

# One colour per genre, dark enough to carry white type at the contrast a grid
# needs. CL15 owns the project's real palette; these are chosen to survive it.
GENRE_COLORS = {
    "beat-em-up": "#8c2f39",
    "platformer": "#1f6f5c",
    "party": "#a8541b",
    "shooter": "#33456b",
    "rpg": "#5b3a7a",
    "sports": "#2d6a4f",
    "racing": "#8a6d1f",
    "puzzle": "#7a3f6d",
    "survival": "#4a4e2f",
    "fighting": "#9c3d2a",
}
NO_GENRE = "#3a3f47"

# Words that carry no identity, so the initials skip them.
SKIPPED = {"a", "an", "the", "of", "and", "e", "o", "in", "to", "for", "vs", "vs."}


def initials(name: str) -> str:
    """Up to two letters that stand for the title in a card-sized space."""
    # A word with no letters or digits ("&", "+", "-") stands for nothing on a card.
    words = [
        w for w in name.split()
        if any(c.isalnum() for c in w) and w.strip(":-").lower() not in SKIPPED
    ]
    letters = [c for w in words for c in w if c.isalnum()][:1]
    if len(words) > 1:
        second = [c for c in words[1] if c.isalnum()][:1]
        letters += second
    elif words:
        letters = [c for c in words[0] if c.isalnum()][:2]
    return "".join(letters).upper() or "?"


def card(game: dict) -> str:
    """One 2:3 typographic cover, as standalone SVG."""
    color = GENRE_COLORS.get(game.get("genre") or "", NO_GENRE)
    label = (game.get("genre") or "no genre").replace("-", " ")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'width="{WIDTH}" height="{HEIGHT}" role="img" '
        f'aria-label="{escape(game["name"])}">'
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{color}"/>'
        f'<text x="{WIDTH / 2}" y="{HEIGHT / 2}" fill="#ffffff" '
        f'font-family="Inter, Segoe UI, system-ui, sans-serif" font-size="86" '
        f'font-weight="700" text-anchor="middle" dominant-baseline="central" '
        f'letter-spacing="2">{escape(initials(game["name"]))}</text>'
        f'<text x="{WIDTH / 2}" y="{HEIGHT - 22}" fill="#ffffff" fill-opacity="0.72" '
        f'font-family="Inter, Segoe UI, system-ui, sans-serif" font-size="13" '
        f'text-anchor="middle" letter-spacing="1">{escape(label)}</text>'
        f"</svg>\n"
    )


def generate(games: list[dict]) -> list[str]:
    """Write one card per game without a packshot; return the ids written."""
    COVERS.mkdir(parents=True, exist_ok=True)
    written = []
    for game in games:
        if game.get("cover_source") not in (None, "generated"):
            continue
        (COVERS / f"{game['id']}.svg").write_text(card(game), encoding="utf-8")
        written.append(game["id"])
    return written


def main() -> int:
    import json

    dataset = ROOT / "data" / "games.json"
    if not dataset.exists():
        print("build-covers: run build_dataset.py first", file=sys.stderr)
        return 1

    games = json.loads(dataset.read_text(encoding="utf-8"))["games"]
    written = generate(games)

    # Cards for games that no longer exist would linger and be served forever.
    keep = {f"{g['id']}.svg" for g in games}
    stale = [p for p in COVERS.glob("*.svg") if p.name not in keep]
    for path in stale:
        path.unlink()

    print(
        f"build-covers: {len(written)} card(s) in "
        f"{COVERS.relative_to(ROOT).as_posix()}, {len(stale)} stale removed",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
