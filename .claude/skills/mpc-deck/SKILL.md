---
name: mpc-deck
description: Turn a pasted MTG deck list into print-ready card images with 1/8" bleed plus an MPC Autofill order.xml for MakePlayingCards. Use when the user pastes a deck list, says "make my deck", "MPC order", "proxies for this list", or mentions MPC Autofill.
---
# MPC deck
Tool: `projects/mpc-deck-builder` (read its README for options).

1. Save the list to `projects/mpc-deck-builder/decks/<deck-name>.txt` (ask for a name if none; kebab-case).
2. Ask only if unclear: DPI (default 600), stock (default S30), foil (default no), custom card back.
3. Run from `projects/mpc-deck-builder`: `uv run mpcdeck decks/<deck-name>.txt -o out/<deck-name> [--dpi N --stock X --foil]`.
   - If Scryfall can't be reached, tell the user to allow `api.scryfall.com` and `cards.scryfall.io` in the cloud
     environment's Network access settings. Don't fake the output.
   - If a card isn't found, show the exact line and ask for the right name or set code.
4. Check: number of PNGs in fronts/ and backs/ matches the order summary, and spot-check one card image by viewing it.
5. Zip it: `cd out && zip -rq <deck-name>.zip <deck-name>`, then send the zip to the user with SendUserFile (display: attach).
6. Tell them: unzip it next to MPC Autofill, run autofill from inside the folder, and say which bracket and stock were used.
Never use `--full-scans` for cards the user will sell. It keeps the official frame and copyright line.
