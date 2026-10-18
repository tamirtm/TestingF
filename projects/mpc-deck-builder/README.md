# mpc-deck-builder
Deck list → finished card images with 1/8" bleed → `order.xml` that **MPC Autofill** uploads to MakePlayingCards.

```
decks/my-deck.txt ──► Scryfall lookup ──► art (art/ override → Scryfall art_crop)
                                 └──► frame (frames/<colour>.png → built-in frame) + text
                                        └──► out/my-deck/{fronts,backs}/*.png + cardback.png + order.xml
```

## Run
```bash
cd projects/mpc-deck-builder
uv run mpcdeck decks/my-deck.txt -o out/my-deck            # 600 DPI, S30 stock
uv run mpcdeck decks/my-deck.txt -o out/my-deck --dpi 800 --stock S33 --foil
uv run mpcdeck - -o out/quick < list.txt                  # deck from stdin
```
Then on your PC: put `out/my-deck/` next to the MPC Autofill program, **run autofill from inside that folder**
(the image paths in order.xml are relative), and it fills the MakePlayingCards project.

## Card spec (matches MPC + MPC Autofill)
| | inches | px @300 | px @600 | px @800 |
|---|---|---|---|---|
| Trim (cut size) | 2.48 × 3.46 | 744 × 1038 | 1488 × 2076 | 1984 × 2768 |
| **With bleed (output)** | **2.72 × 3.70** | **816 × 1110** | **1632 × 2220** | **2176 × 2960** |
Bleed is 0.12" per side (MPC's "1/8 inch"). The frame's black border runs through the bleed so cuts never show white.

## Deck list formats
`4 Lightning Bolt` · `4x Lightning Bolt` · `1 Sol Ring (C21) 263` · `1 Delver of Secrets // Insectile Aberration` ·
`*F*` markers and `Deck` / `Sideboard` / `Commander` headers are fine (Moxfield, Archidekt, MTGA exports).
Double-faced cards get their back face in `backs/`; everything else gets `cardback.png`.

## Customise
- **Art:** drop `art/<Card Name>.png|jpg` to override Scryfall art for that card. Use this for commissioned or licensed art, or art you made.
- **Frames:** drop `frames/<key>.png`, where key is one of `W U B R G gold artifact land`, sized to the bleed canvas (any DPI) with a
  transparent art window. Text boxes are positioned by `LAYOUT` in `mpcdeck/render.py`; adjust them to fit your frames.
- **Fonts:** `fonts/regular.ttf`, `fonts/bold.ttf`, `fonts/italic.ttf`.
- **Card back:** `--cardback my-back.png` (trim size or bleed size; bleed is added if missing).
- `--full-scans`: skips rendering and uses Scryfall's full card scan plus edge-extended bleed. **Playtest only.** See the note below.

## Notes
- Scryfall requests are cached in `.cache/scryfall` and rate-limited to Scryfall's ~10 requests per second.
  The cloud environment must allow `api.scryfall.com` and `cards.scryfall.io`.
- Scryfall's `art_crop` is ~626 px wide, which is soft at 600+ DPI. For sharp prints, upscale the art (e.g. Real-ESRGAN) into `art/`.
- **Rights:** card names, rules text, art and official frames belong to Wizards of the Coast and the artists.
  Personal playtest proxies are common. Selling cards that use official art or frames is infringement. MPC also rejects
  files with visible copyright lines (which `--full-scans` keeps, as Scryfall requires). For anything you sell,
  use your own frames (the built-in frame is original) and art you own or license, via `art/`.
