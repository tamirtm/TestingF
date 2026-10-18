"""Card geometry (MakePlayingCards poker size) and bleed helpers."""
from PIL import Image

TRIM_IN = (2.48, 3.46)   # MPC poker card, 63 x 88 mm
BLEED_IN = 0.12          # MPC's 1/8" bleed per side (template 2.72 x 3.70 in; MPC Autofill uses 1110 px = 300 DPI)


def canvas_px(dpi: int) -> tuple[int, int]:
    return round((TRIM_IN[0] + 2 * BLEED_IN) * dpi), round((TRIM_IN[1] + 2 * BLEED_IN) * dpi)


def bleed_px(dpi: int) -> int:
    return round(BLEED_IN * dpi)


def add_bleed(img: Image.Image, dpi: int) -> Image.Image:
    """Turn a trim-size card image (no bleed) into a full-bleed image by extending its edge pixels outward."""
    w, h = canvas_px(dpi)
    b = bleed_px(dpi)
    inner = img.convert("RGB").resize((w - 2 * b, h - 2 * b), Image.LANCZOS)
    out = Image.new("RGB", (w, h))
    out.paste(inner, (b, b))
    iw, ih = inner.size
    out.paste(inner.crop((0, 0, iw, 1)).resize((iw, b)), (b, 0))              # top
    out.paste(inner.crop((0, ih - 1, iw, ih)).resize((iw, b)), (b, h - b))    # bottom
    left = out.crop((b, 0, b + 1, h)).resize((b, h))
    right = out.crop((w - b - 1, 0, w - b, h)).resize((b, h))
    out.paste(left, (0, 0))
    out.paste(right, (w - b, 0))
    return out
