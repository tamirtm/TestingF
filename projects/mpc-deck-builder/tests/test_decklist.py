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


def test_slug_split_card():
    from mpcdeck.cli import slug
    assert slug("Fire // Ice") == "Fire - Ice"
    assert slug("Lim-Dûl's Vault") == "Lim-Dl's Vault"


def test_archidekt_tags_and_duplicates():
    text = """1x Mox Sapphire (ovnt) 2016NA [Ramp]
1x Crystal Spray [Custom Card] #CustomCard
1x Crystal Spray [Custom Card] #CustomCard
1x Savannah (olgc) 2017NA [Land]
1x Savannah (olgc) 2017NA [Land]
"""
    assert parse(text) == [
        Entry(1, "Mox Sapphire", "ovnt", "2016NA"),
        Entry(2, "Crystal Spray", custom=True),
        Entry(2, "Savannah", "olgc", "2017NA"),
    ]
