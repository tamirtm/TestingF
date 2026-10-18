"""mpcdeck: deck list -> bleed-ready PNGs + MPC Autofill order.xml.

  mpcdeck deck.txt -o out/my-deck [--dpi 600] [--stock S30] [--foil] [--art art/] [--frames frames/]
          [--cardback back.png] [--full-scans]

Art priority per card: art/<Card Name>.(png|jpg) override  ->  Scryfall art_crop.
--full-scans: skip rendering; use Scryfall's full card image + edge-extended bleed (playtest only).
"""
import argparse
import io
import re
import sys
from pathlib import Path

from PIL import Image

from . import decklist, order
from .bleed import add_bleed
from .render import cardback, render
from .scryfall import Scryfall


def slug(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9 ,'\-]+", "", name).strip()


def faces(card: dict) -> list[dict]:
    """Front (and back, for double-faced layouts) faces, each with art URL + artist."""
    if "card_faces" in card and "image_uris" not in card:          # transform / MDFC / flip-both-sides
        return [{**f, "artist": f.get("artist", card.get("artist"))} for f in card["card_faces"]][:2]
    if "card_faces" in card:                                        # split / adventure: one image, merged text
        f0 = card["card_faces"][0]
        merged = {**card, "mana_cost": f0.get("mana_cost", ""), "type_line": card.get("type_line", f0.get("type_line", "")),
                  "oracle_text": "\n".join(f"{f['name']} {f.get('mana_cost','')}: {f.get('oracle_text','')}" for f in card["card_faces"]),
                  "power": f0.get("power"), "toughness": f0.get("toughness")}
        return [merged]
    return [card]


def local_art(art_dir: Path | None, name: str) -> bytes | None:
    if not art_dir:
        return None
    for ext in ("png", "jpg", "jpeg", "webp"):
        p = art_dir / f"{name}.{ext}"
        if p.exists():
            return p.read_bytes()
    return None


def build_deck(text: str, out: Path, sf: Scryfall, dpi: int = 600, stock: str = "S30", foil: bool = False,
               art_dir: Path | None = None, frames_dir: Path | None = None, back_path: Path | None = None,
               full_scans: bool = False, log=print) -> Path:
    entries = decklist.parse(text)
    cards = sf.cards(entries)
    (out / "fronts").mkdir(parents=True, exist_ok=True)
    fronts, backs, slot = [], [], 0
    for e in entries:
        fs = faces(cards[e])
        slots = list(range(slot, slot + e.qty))
        slot += e.qty
        for side, face in enumerate(fs):
            fname = slug(face["name"]) + (f" ({e.set}-{e.number})" if e.number else "") + ".png"
            sub = "fronts" if side == 0 else "backs"
            rel = f"{sub}/{fname}"
            dest = out / rel
            dest.parent.mkdir(exist_ok=True)
            if not dest.exists():
                if full_scans:
                    url = (face.get("image_uris") or cards[e].get("image_uris"))["png"]
                    img = add_bleed(Image.open(io.BytesIO(sf.image(url))), dpi)
                else:
                    art = local_art(art_dir, face["name"])
                    if art is None and (face.get("image_uris") or cards[e].get("image_uris")):
                        art = sf.image((face.get("image_uris") or cards[e]["image_uris"])["art_crop"])
                    img = render(face, art, dpi, frames_dir)
                img.save(dest, dpi=(dpi, dpi), optimize=True)
                log(f"  {rel}")
            (fronts if side == 0 else backs).append((rel, slots))

    back_rel = "cardback.png"
    if back_path:
        add_bleed(Image.open(back_path), dpi).save(out / back_rel, dpi=(dpi, dpi))
    else:
        cardback(dpi).save(out / back_rel, dpi=(dpi, dpi))
    xml = order.build(fronts, backs, back_rel, total=slot, stock=stock, foil=foil)
    (out / "order.xml").write_text(xml)
    log(f"{slot} cards, {len(fronts)} unique fronts, {len(backs)} backs -> {out/'order.xml'} (bracket {order.bracket_for(slot)})")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="mpcdeck", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("deck", type=Path, help="deck list file, or - for stdin")
    ap.add_argument("-o", "--out", type=Path, required=True)
    ap.add_argument("--dpi", type=int, default=600)
    ap.add_argument("--stock", choices=list(order.STOCKS), default="S30")
    ap.add_argument("--foil", action="store_true")
    ap.add_argument("--art", type=Path, default=Path("art"))
    ap.add_argument("--frames", type=Path, default=Path("frames"))
    ap.add_argument("--cardback", type=Path)
    ap.add_argument("--full-scans", action="store_true")
    ap.add_argument("--cache", type=Path, default=Path(".cache/scryfall"))
    a = ap.parse_args(argv)
    text = sys.stdin.read() if str(a.deck) == "-" else a.deck.read_text()
    build_deck(text, a.out, Scryfall(a.cache), a.dpi, a.stock, a.foil, a.art, a.frames, a.cardback, a.full_scans)
    return 0


if __name__ == "__main__":
    sys.exit(main())
