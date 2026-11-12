#!/usr/bin/env bash
# Copy the skills a vendored Claude Code plugin ships into .claude/skills/, verbatim.
#   scripts/install-vendor-skills.sh <vendor-name> [--check] [--skip name,name]
# Reads vendor/<name>/.claude-plugin/plugin.json ("skills" list). --check only reports drift (exit 1).
# Never overwrites a skill that is not already recorded in .claude/skills/VENDORED.tsv.
set -euo pipefail
root=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
name=${1:?usage: install-vendor-skills.sh <vendor-name> [--check] [--skip a,b]}; shift
check=0; skip=""
while [ $# -gt 0 ]; do case "$1" in --check) check=1 ;; --skip) skip=",$2,"; shift ;; *) echo "unknown arg $1" >&2; exit 2 ;; esac; shift; done
src="$root/vendor/$name"; dest="$root/.claude/skills"; rec="$dest/VENDORED.tsv"
[ -f "$src/.claude-plugin/plugin.json" ] || { echo "no plugin.json in vendor/$name (run scripts/vendor.sh --restore?)" >&2; exit 2; }
lic=$("$root/scripts/license-check.sh" "$src" --short)
case "$lic" in MIT|BSD|ISC|Unlicense|Apache-2.0) ;; *) echo "license $lic: not copying. Ask the human." >&2; exit 2 ;; esac
commit=$(git -C "$src" rev-parse HEAD)
[ -f "$rec" ] || printf 'skill\tvendor\tcommit\tpath\n' > "$rec"
drift=0; n=0
while read -r rel; do
  s=$(basename "$rel")
  case "$skip" in *",$s,"*) echo "skip    $s"; continue ;; esac
  if [ -e "$dest/$s" ] && ! grep -q "^$s	$name	" "$rec"; then
    echo "‼️ $s exists in .claude/skills and is not from $name; refusing to overwrite" >&2; drift=1; continue
  fi
  if [ $check = 1 ]; then
    diff -rq "$src/$rel" "$dest/$s" >/dev/null 2>&1 || { echo "drift   $s"; drift=1; }
  else
    rm -rf "${dest:?}/$s"; cp -R "$src/$rel" "$dest/$s"
    grep -v "^$s	" "$rec" > "$rec.tmp" || true; mv "$rec.tmp" "$rec"
    printf '%s\t%s\t%s\t%s\n' "$s" "$name" "$commit" "$rel" >> "$rec"
  fi
  n=$((n+1))
done < <(python3 -c 'import json,sys; [print(p.removeprefix("./")) for p in json.load(open(sys.argv[1]))["skills"]]' "$src/.claude-plugin/plugin.json")
[ $check = 1 ] && echo "checked $n skill(s) from $name@${commit:0:10}" || echo "installed $n skill(s) from $name@${commit:0:10} (license: $lic)"
exit $drift
