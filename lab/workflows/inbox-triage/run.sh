#!/usr/bin/env bash
# Triage text notes into folders by keyword rules. DRY_RUN=1 (default) prints moves instead of doing them.
#   ./run.sh <inbox-dir> [dest-root]
set -euo pipefail
inbox=${1:?usage: run.sh <inbox-dir> [dest-root]}; dest=${2:-./triaged}; DRY_RUN=${DRY_RUN:-1}
classify() {
  local t; t=$(tr '[:upper:]' '[:lower:]' < "$1")
  case "$t" in
    *invoice*|*receipt*|*payment*) echo finance ;;
    *bug*|*error*|*stack\ trace*)  echo dev ;;
    *meeting*|*call\ with*)        echo meetings ;;
    *) echo review ;;
  esac
}
for f in "$inbox"/*; do
  [ -f "$f" ] || continue
  c=$(classify "$f")
  if [ "$DRY_RUN" = 1 ]; then echo "$(basename "$f") -> $c"
  else mkdir -p "$dest/$c" && mv "$f" "$dest/$c/" && echo "$(date -Is) moved $(basename "$f") -> $c"; fi
done
