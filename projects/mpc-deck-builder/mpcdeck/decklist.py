"""Parse deck lists (MTGA / Moxfield / Archidekt / plain "4 Card Name") into entries."""
import re
from dataclasses import dataclass

HEADERS = {"deck", "main", "mainboard", "sideboard", "commander", "companion", "maybeboard", "tokens"}
LINE = re.compile(
    r"^(?P<qty>\d+)\s*x?\s+"            # 4 / 4x
    r"(?P<name>.+?)"                     # card name (may contain //)
    r"(?:\s+\((?P<set>[A-Za-z0-9]+)\)"   # optional (SET)
    r"(?:\s+(?P<num>[A-Za-z0-9\-★]+))?)?"  # optional collector number
    r"(?:\s+\*[A-Z]+\*)*\s*$"            # optional *F* / *E* markers
)
TRAILING = re.compile(r"\s+(\[[^\]]*\]|#\S+)\s*$")   # Archidekt "[Land]" categories, "#CustomCard" tags


@dataclass(frozen=True)
class Entry:
    qty: int
    name: str
    set: str | None = None
    number: str | None = None
    custom: bool = False        # tagged [Custom Card] / #CustomCard -> prefer custom/<name>.png


def parse(text: str) -> list[Entry]:
    entries: list[Entry] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", "//")) or line.lower().rstrip(":") in HEADERS:
            continue
        tags = []
        while (t := TRAILING.search(line)):
            tags.append(t[1].strip("[]#").lower())
            line = line[:t.start()]
        m = LINE.match(line)
        if not m:
            raise ValueError(f"Can't parse deck line: {raw!r}")
        custom = any("custom" in t.replace(" ", "") for t in tags)
        entries.append(Entry(int(m["qty"]), m["name"].strip(), (m["set"] or None) and m["set"].lower(), m["num"], custom))
    return merge(entries)


def merge(entries: list[Entry]) -> list[Entry]:
    """Combine duplicate lines (same card + printing) into one entry, keeping first-seen order."""
    totals: dict[tuple, Entry] = {}
    for e in entries:
        key = (e.name.lower(), e.set, e.number, e.custom)
        totals[key] = Entry(totals[key].qty + e.qty, e.name, e.set, e.number, e.custom) if key in totals else e
    return list(totals.values())
