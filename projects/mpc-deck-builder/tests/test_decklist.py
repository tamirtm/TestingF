import pytest

from mpcdeck.decklist import Entry, parse


def test_formats():
    text = """Deck
4 Lightning Bolt
4x Llanowar Elves
1 Sol Ring (C21) 263
2 Delver of Secrets // Insectile Aberration (ISD) 51 *F*
// comment

Sideboard
10 Mountain
"""
    assert parse(text) == [
        Entry(4, "Lightning Bolt"), Entry(4, "Llanowar Elves"), Entry(1, "Sol Ring", "c21", "263"),
        Entry(2, "Delver of Secrets // Insectile Aberration", "isd", "51"), Entry(10, "Mountain"),
    ]


def test_bad_line():
    with pytest.raises(ValueError):
        parse("Lightning Bolt")
