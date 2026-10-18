from xml.etree import ElementTree as ET

import pytest

from mpcdeck.order import bracket_for, build


def test_brackets():
    assert bracket_for(1) == 18
    assert bracket_for(60) == 72
    assert bracket_for(100) == 108
    with pytest.raises(ValueError):
        bracket_for(613)


def test_xml_shape():
    xml = build([("fronts/A.png", [0, 1]), ("fronts/B.png", [2])], [("backs/C.png", [2])], "cardback.png", total=3)
    root = ET.fromstring(xml)
    assert root.findtext("details/quantity") == "3"
    assert root.findtext("details/bracket") == "18"
    assert root.findtext("details/stock") == "(S30) Standard Smooth"
    cards = root.findall("fronts/card")
    assert [c.findtext("id") for c in cards] == ["fronts/A.png", "fronts/B.png"]
    assert cards[0].findtext("slots") == "0,1"
    assert cards[0].findtext("sourceType") == "Local File"
    assert root.findtext("backs/card/slots") == "2"
    assert root.findtext("cardback") == "cardback.png"
