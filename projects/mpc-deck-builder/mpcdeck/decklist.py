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


@dataclass(frozen=True)
class Entry:
    qty: int
    name: str
    set: str | None = None
    number: str | None = None


def parse(text: str) -> list[Entry]:
    entries: list[Entry] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", "//")) or line.lower().rstrip(":") in HEADERS:
            continue
        m = LINE.match(line)
        if not m:
            raise ValueError(f"Can't parse deck line: {raw!r}")
        entries.append(Entry(int(m["qty"]), m["name"].strip(), (m["set"] or None) and m["set"].lower(), m["num"]))
    return entries
