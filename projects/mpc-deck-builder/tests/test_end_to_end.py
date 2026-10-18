from xml.etree import ElementTree as ET

from PIL import Image

from mpcdeck.cli import build_deck

DECK = """4 Lightning Bolt
4 Llanowar Elves
2 Delver of Secrets // Insectile Aberration
10 Mountain
"""


def test_build_deck(tmp_path, sf):
    out = build_deck(DECK, tmp_path / "out", sf, dpi=300, log=lambda *_: None)
    root = ET.parse(out / "order.xml").getroot()
    assert root.findtext("details/quantity") == "20"
    assert root.findtext("details/bracket") == "36"
    fronts = {c.findtext("name"): c.findtext("slots") for c in root.findall("fronts/card")}
    assert fronts["Lightning Bolt.png"] == "0,1,2,3"
    assert fronts["Mountain.png"] == ",".join(map(str, range(10, 20)))
    assert root.findtext("backs/card/name") == "Insectile Aberration.png"
    assert root.findtext("backs/card/slots") == "8,9"
    for c in root.iter("card"):
        img = Image.open(out / c.findtext("id"))
        assert img.size == (816, 1110)
    assert Image.open(out / "cardback.png").size == (816, 1110)


def test_art_override_and_full_scans(tmp_path, sf):
    art = tmp_path / "art"
    art.mkdir()
    Image.new("RGB", (400, 300), (10, 200, 10)).save(art / "Lightning Bolt.png")
    out = build_deck("1 Lightning Bolt", tmp_path / "o1", sf, dpi=300, art_dir=art, log=lambda *_: None)
    img = Image.open(out / "fronts" / "Lightning Bolt.png")
    assert img.getpixel((408, 300)) == (10, 200, 10)       # local art used inside the art box

    out2 = build_deck("1 Lightning Bolt", tmp_path / "o2", sf, dpi=300, full_scans=True, log=lambda *_: None)
    assert Image.open(out2 / "fronts" / "Lightning Bolt.png").size == (816, 1110)


def test_custom_design_used_as_is(tmp_path, sf):
    custom = tmp_path / "custom"
    custom.mkdir()
    Image.new("RGB", (744, 1038), (200, 30, 200)).save(custom / "Lightning Bolt.png")
    out = build_deck("2x Lightning Bolt [Custom Card] #CustomCard", tmp_path / "o", sf, dpi=300,
                     custom_dir=custom, log=lambda *_: None)
    img = Image.open(out / "fronts" / "Lightning Bolt.png")
    assert img.size == (816, 1110) and img.getpixel((408, 555)) == (200, 30, 200)
    root = ET.parse(out / "order.xml").getroot()
    assert root.findtext("fronts/card/slots") == "0,1"
