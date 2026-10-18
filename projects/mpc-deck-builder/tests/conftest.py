import io
import json
from pathlib import Path

import pytest
from PIL import Image

from mpcdeck.scryfall import Scryfall

FIX = json.loads((Path(__file__).parent / "fixtures" / "cards.json").read_text())


def fake_fetch(url: str, body: dict | None = None) -> bytes:
    """Offline stand-in for Scryfall: collection lookups from fixtures, images as solid-colour PNGs."""
    if body is not None:
        data, missing = [], []
        for ident in body["identifiers"]:
            card = FIX.get(ident.get("name", "").lower())
            (data.append(card) if card else missing.append(ident))
        return json.dumps({"data": data, "not_found": missing}).encode()
    color = {"bolt": "#c33", "elves": "#3a3", "mtn": "#a63"}.get(url.rsplit("/", 1)[-1].split(".")[0], "#36c")
    size = (745, 1040) if "/png/" in url else (626, 457)
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, "PNG")
    return buf.getvalue()


@pytest.fixture
def sf(tmp_path):
    return Scryfall(tmp_path / "cache", fetch=fake_fetch, delay=0)
