"""Minimal Scryfall client: batched card lookup + image download, cached on disk, polite rate limit."""
import hashlib
import json
import time
import urllib.request
from pathlib import Path
from typing import Callable

from .decklist import Entry

API = "https://api.scryfall.com"
HEADERS = {"User-Agent": "MPCDeckBuilder/0.1", "Accept": "application/json;q=0.9,*/*;q=0.8"}


def _http(url: str, body: dict | None = None) -> bytes:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers={**HEADERS, **({"Content-Type": "application/json"} if data else {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


class Scryfall:
    def __init__(self, cache_dir: Path, fetch: Callable[[str, dict | None], bytes] = _http, delay: float = 0.1):
        self.cache = Path(cache_dir)
        self.cache.mkdir(parents=True, exist_ok=True)
        self.fetch, self.delay = fetch, delay

    def _cached(self, key: str, url: str, body: dict | None = None) -> bytes:
        path = self.cache / hashlib.sha1(key.encode()).hexdigest()
        if path.exists():
            return path.read_bytes()
        time.sleep(self.delay)  # Scryfall asks for 50-100 ms between requests
        data = self.fetch(url, body)
        path.write_bytes(data)
        return data

    def cards(self, entries: list[Entry]) -> dict[Entry, dict]:
        """Resolve entries to Scryfall card objects via /cards/collection (75 per request)."""
        out: dict[Entry, dict] = {}
        for i in range(0, len(entries), 75):
            chunk = entries[i:i + 75]
            ids = [{"set": e.set, "collector_number": e.number} if e.set and e.number
                   else {"name": e.name, "set": e.set} if e.set else {"name": e.name.split(" // ")[0]}
                   for e in chunk]
            body = {"identifiers": ids}
            res = json.loads(self._cached(json.dumps(body, sort_keys=True), f"{API}/cards/collection", body))
            if res.get("not_found"):
                raise LookupError(f"Scryfall couldn't find: {res['not_found']}")
            for e, card in zip(chunk, res["data"]):
                out[e] = card
        return out

    def image(self, url: str) -> bytes:
        return self._cached(url, url)
