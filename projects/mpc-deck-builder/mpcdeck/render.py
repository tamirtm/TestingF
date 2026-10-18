"""Compose a full-bleed card: art + frame + text.

Frames: by default an original, programmatic frame is drawn (no third-party assets).
To use your own frames (e.g. exported from a Card Conjurer local install, or your own designs),
drop PNGs in frames/ named by colour key (W U B R G gold artifact land) with a transparent art
window, sized to the bleed canvas at any DPI. Text boxes come from LAYOUT (fractions of the canvas).
"""
import io
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .bleed import canvas_px

# Boxes as (left, top, right, bottom) fractions of the full-bleed canvas.
LAYOUT = {
    "name":   (0.085, 0.072, 0.915, 0.122),
    "art":    (0.090, 0.130, 0.910, 0.535),
    "type":   (0.085, 0.543, 0.915, 0.590),
    "text":   (0.095, 0.600, 0.905, 0.865),
    "pt":     (0.730, 0.860, 0.915, 0.905),
    "artist": (0.090, 0.910, 0.700, 0.935),
}
FRAME_COLORS = {
    "W": "#EDE3C8", "U": "#3B78B8", "B": "#4A4442", "R": "#C4513A", "G": "#3C7F52",
    "gold": "#C9A24B", "artifact": "#9AA3AD", "land": "#9C8064",
}
MANA_COLORS = {"W": "#F8F1D8", "U": "#AAD4F0", "B": "#BDB3AE", "R": "#F2A68C", "G": "#9ED3A8", "C": "#D5D0CC"}
SYMBOL = re.compile(r"\{([^}]+)\}")
GLUE = "\x00"  # token prefix: no space before it


def frame_key(card: dict) -> str:
    if "Land" in card.get("type_line", ""):
        return "land"
    colors = card.get("colors") or []
    if len(colors) > 1:
        return "gold"
    return colors[0] if colors else "artifact"


def _font(size: int, bold: bool = False, italic: bool = False) -> ImageFont.FreeTypeFont:
    here = Path(__file__).resolve().parent.parent / "fonts"
    style = "bold" if bold else "italic" if italic else "regular"
    dv = {"bold": "-Bold", "italic": "-Italic", "regular": ""}[style]
    for p in [here / f"{style}.ttf",
              Path(f"/usr/share/fonts/truetype/dejavu/DejaVuSerif{dv}.ttf"),
              Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf")]:     # no italic installed -> regular
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default(size=size)


def _box(name: str, w: int, h: int) -> tuple[int, int, int, int]:
    l, t, r, b = LAYOUT[name]
    return round(l * w), round(t * h), round(r * w), round(b * h)


def _symbol(draw: ImageDraw.ImageDraw, x: int, y: int, size: int, sym: str) -> None:
    fill = MANA_COLORS.get(sym, MANA_COLORS["C"])
    draw.ellipse((x, y, x + size, y + size), fill=fill, outline="#222", width=max(1, size // 14))
    label = "↷" if sym == "T" else sym
    f = _font(int(size * (0.62 if len(label) < 2 else 0.45)), bold=True)
    draw.text((x + size / 2, y + size / 2), label, font=f, fill="#111", anchor="mm")


def _tokens(text: str) -> list[str]:
    """Split into words and {X} symbols, keeping symbols as separate tokens."""
    out: list[str] = []
    pos = 0
    pieces = []
    for m in SYMBOL.finditer(text):
        pieces += [text[pos:m.start()], "{" + m[1] + "}"]
        pos = m.end()
    pieces.append(text[pos:])
    prev = " "
    for piece in pieces:
        if not piece:
            continue
        if SYMBOL.fullmatch(piece):
            out.append((GLUE if out and not prev.endswith(" ") else "") + piece)
            prev = piece
            continue
        prev = piece
        words = piece.split(" ")
        if out and words[0]:            # text touching the previous symbol, e.g. "{T}:" -> glue ":"
            words[0] = GLUE + words[0]
        out += [w for w in words if w]
    return out


def _is_sym(tok: str) -> bool:
    return bool(SYMBOL.fullmatch(tok.lstrip(GLUE)))


def _measure(tok: str, font: ImageFont.FreeTypeFont) -> int:
    return font.size if _is_sym(tok) else round(font.getlength(tok.lstrip(GLUE)))


def _gap(tok: str, space: int) -> int:
    return 0 if tok.startswith(GLUE) else space


def _layout_text(text: str, font, width: int) -> list[list[str]]:
    lines: list[list[str]] = []
    for para in text.split("\n"):
        line, lw = [], 0
        space = round(font.getlength(" "))
        for tok in _tokens(para):
            tw = _measure(tok, font)
            if line and lw + _gap(tok, space) + tw > width:
                lines.append(line)
                line, lw = [], 0
            lw += (_gap(tok, space) if line else 0) + tw
            line.append(tok)
        lines.append(line)
    return lines


def _draw_rules(draw, text: str, box, max_size: int, flavor: str = "") -> None:
    l, t, r, b = box
    pad = round((r - l) * 0.035)
    l, t, r, b = l + pad, t + pad, r - pad, b - pad
    rules_lines = 0
    size = max_size
    while size > 10:
        font = _font(size)
        italic = _font(size, italic=True)
        rules = _layout_text(text, font, r - l) if text else []
        flav = _layout_text(flavor, italic, r - l) if flavor else []
        lines = rules + flav
        rules_lines = len(rules)
        line_h = round(size * 1.22)
        if line_h * len(lines) <= b - t:
            break
        size -= 2
    y = t + max(0, ((b - t) - line_h * len(lines)) // 2)
    space = round(font.getlength(" "))
    for n, line in enumerate(lines):
        i_flavor = n >= rules_lines
        if i_flavor and n == rules_lines and rules_lines:
            draw.line((l, y + line_h * 0.15, r, y + line_h * 0.15), fill="#999", width=max(1, size // 12))
            y += round(line_h * 0.3)
        x = l
        for i, tok in enumerate(line):
            if i:
                x += _gap(tok, space)
            if _is_sym(tok):
                _symbol(draw, x, y + round(size * 0.12), size, tok.lstrip(GLUE)[1:-1])
            else:
                draw.text((x, y), tok.lstrip(GLUE), font=italic if i_flavor else font, fill="#111")
            x += _measure(tok, font)
        y += line_h


def _fit_art(art: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Cover-fit: scale to fill the box, centre-crop the overflow."""
    bw, bh = size
    scale = max(bw / art.width, bh / art.height)
    art = art.convert("RGB").resize((round(art.width * scale), round(art.height * scale)), Image.LANCZOS)
    left, top = (art.width - bw) // 2, (art.height - bh) // 2
    return art.crop((left, top, left + bw, top + bh))


def render(face: dict, art_bytes: bytes | None, dpi: int, frames_dir: Path | None = None) -> Image.Image:
    """Render one card face. `face` uses Scryfall field names (name, mana_cost, type_line, oracle_text, ...)."""
    w, h = canvas_px(dpi)
    key = frame_key(face)
    card = Image.new("RGB", (w, h), "#111111")       # black outer border, extends through the bleed
    d = ImageDraw.Draw(card)

    al, at, ar, ab = _box("art", w, h)
    if art_bytes:
        card.paste(_fit_art(Image.open(io.BytesIO(art_bytes)), (ar - al, ab - at)), (al, at))
    else:
        d.rectangle((al, at, ar, ab), fill="#777")

    custom = frames_dir / f"{key}.png" if frames_dir else None
    if custom and custom.exists():
        overlay = Image.open(custom).convert("RGBA").resize((w, h), Image.LANCZOS)
        card.paste(overlay, (0, 0), overlay)
    else:
        color = FRAME_COLORS[key]
        m = round(w * 0.065)                          # frame inset from canvas edge (bleed + border)
        frame = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        fd = ImageDraw.Draw(frame)
        fd.rounded_rectangle((m, m, w - m, h - m), radius=round(w * 0.03), fill=color)
        fd.rectangle((al, at, ar, ab), fill=(0, 0, 0, 0))           # art window
        card.paste(frame, (0, 0), frame)
        d.rectangle((al, at, ar, ab), outline="#222", width=max(2, w // 300))
        for name in ("name", "type"):
            d.rounded_rectangle(_box(name, w, h), radius=round(h * 0.012), fill="#F4EFE6", outline="#222", width=max(2, w // 400))
        d.rectangle(_box("text", w, h), fill="#FBF8F2", outline="#222", width=max(2, w // 400))

    # name + mana cost
    nl, nt, nr, nb = _box("name", w, h)
    pad = round(w * 0.015)
    nsize = round((nb - nt) * 0.58)
    cost = SYMBOL.findall(face.get("mana_cost", ""))
    sym = round((nb - nt) * 0.62)
    x = nr - pad - len(cost) * (sym + 2)
    for s in cost:
        _symbol(d, x, nt + ((nb - nt) - sym) // 2, sym, s)
        x += sym + 2
    nfont = _font(nsize, bold=True)
    while nfont.getlength(face["name"]) > (nr - nl) - 2 * pad - len(cost) * (sym + 2) and nsize > 10:
        nsize -= 2
        nfont = _font(nsize, bold=True)
    d.text((nl + pad, (nt + nb) / 2), face["name"], font=nfont, fill="#111", anchor="lm")

    tl, tt, tr, tb = _box("type", w, h)
    d.text((tl + pad, (tt + tb) / 2), face.get("type_line", ""), font=_font(round((tb - tt) * 0.5), bold=True), fill="#111", anchor="lm")

    text, flavor = face.get("oracle_text", ""), face.get("flavor_text", "")
    if text or flavor:
        _draw_rules(d, text, _box("text", w, h), max_size=round(h * 0.026), flavor=flavor)

    if face.get("power") is not None:
        pl, pt_, pr, pb = _box("pt", w, h)
        d.rounded_rectangle((pl, pt_, pr, pb), radius=round(h * 0.01), fill="#F4EFE6", outline="#222", width=max(2, w // 400))
        d.text(((pl + pr) / 2, (pt_ + pb) / 2), f"{face['power']}/{face['toughness']}",
               font=_font(round((pb - pt_) * 0.62), bold=True), fill="#111", anchor="mm")

    if face.get("artist"):
        xl, xt, xr, xb = _box("artist", w, h)
        d.text((xl, (xt + xb) / 2), f"Illus. {face['artist']}", font=_font(round((xb - xt) * 0.7)), fill="#EEE", anchor="lm")
    return card


def cardback(dpi: int, label: str = "") -> Image.Image:
    w, h = canvas_px(dpi)
    img = Image.new("RGB", (w, h), "#1B1F2A")
    d = ImageDraw.Draw(img)
    m = round(w * 0.09)
    d.rounded_rectangle((m, m, w - m, h - m), radius=round(w * 0.05), outline="#C9A24B", width=max(3, w // 120))
    if label:
        d.text((w / 2, h / 2), label, font=_font(round(w * 0.08), bold=True), fill="#C9A24B", anchor="mm")
    return img
