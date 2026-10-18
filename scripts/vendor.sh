#!/usr/bin/env bash
# Vendor upstream code at a pinned commit.
#   scripts/vendor.sh <git-url> [name] [ref]   fetch and pin a new upstream
#   scripts/vendor.sh --restore                re-fetch everything in manifest.tsv
set -euo pipefail
root=$(git -C "$(dirname "$0")" rev-parse --show-toplevel); m="$root/vendor/manifest.tsv"

fetch() { # url name commit-or-ref
  local dest="$root/vendor/$2"; rm -rf "$dest"
  git clone -q --filter=blob:none "$1" "$dest"
  git -C "$dest" checkout -q "$3"
}

if [ "${1:-}" = "--restore" ]; then
  tail -n +2 "$m" | while IFS=$'\t' read -r name url commit _; do
    echo "restore $name@${commit:0:10}"; fetch "$url" "$name" "$commit"; done
  exit 0
fi

url=${1:?usage: vendor.sh <git-url> [name] [ref]}
name=${2:-$(basename "$url" .git)}; ref=${3:-HEAD}
fetch "$url" "$name" "$ref"
commit=$(git -C "$root/vendor/$name" rev-parse HEAD)
lic=$("$root/scripts/license-check.sh" "$root/vendor/$name" --short)
grep -v "^$name	" "$m" > "$m.tmp" || true; mv "$m.tmp" "$m"
printf '%s\t%s\t%s\t%s\n' "$name" "$url" "$commit" "$lic" >> "$m"
echo "vendored $name @ ${commit:0:10} (license: $lic)"
