#!/usr/bin/env bash
# Identify a directory's license and what it lets us do.
#   scripts/license-check.sh <dir> [--short]
set -euo pipefail
dir=${1:?usage: license-check.sh <dir> [--short]}
f=$(find "$dir" -maxdepth 1 -iregex '.*/\(license\|licence\|copying\|unlicense\)\(\.[a-z]+\)?' | head -1)
if [ -z "$f" ]; then
  id="NONE"
else
  t=$(tr -s '[:space:]' ' ' < "$f" | tr '[:upper:]' '[:lower:]')
  case "$t" in
    *"gnu affero general public license"*)          id="AGPL" ;;
    *"gnu lesser general public license"*)          id="LGPL" ;;
    *"gnu general public license"*)                 id="GPL" ;;
    *"mozilla public license"*)                     id="MPL-2.0" ;;
    *"apache license"*)                             id="Apache-2.0" ;;
    *"permission is hereby granted, free of charge"*) id="MIT" ;;
    *"redistribution and use in source and binary forms"*) id="BSD" ;;
    *"isc license"*|*"permission to use, copy, modify, and/or distribute"*) id="ISC" ;;
    *"this is free and unencumbered software"*)     id="Unlicense" ;;
    *) id="UNKNOWN" ;;
  esac
fi
[ "${2:-}" = "--short" ] && { echo "$id"; exit 0; }
case "$id" in
  MIT|BSD|ISC|Unlicense) v="OK to copy/adapt. Keep the copyright + license text in NOTICE.md." ;;
  Apache-2.0) v="OK to copy/adapt. Keep LICENSE + any NOTICE file, and state that you changed files." ;;
  MPL-2.0)    v="File-level copyleft: modified MPL files stay MPL and public; your other files are yours." ;;
  LGPL)       v="Link to it as a library freely; changes to the library itself must be shared." ;;
  GPL)        v="STOP: copying makes your whole project GPL. Ask the human first." ;;
  AGPL)       v="STOP: like GPL, and also applies to network/SaaS use. Ask the human first." ;;
  NONE)       v="STOP: no license = all rights reserved. Read and learn only; do not copy code." ;;
  *)          v="Unrecognised license in ${f}. Read it and ask the human." ;;
esac
echo "license: $id ${f:+($f)}"; echo "$v"
