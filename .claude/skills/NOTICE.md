# Third-party skills in this folder

The skills listed in `VENDORED.tsv` are copied verbatim (no changes) from
[mattpocock/skills](https://github.com/mattpocock/skills) at commit
`4ae2317ddb22b046e26455e4f9c9b3aaaf62212d` (plugin `mattpocock-skills` v1.3.2), MIT license.

- Files taken: the 27 skills the plugin's `.claude-plugin/plugin.json` ships, minus `code-review`
  (skipped so it does not collide with Claude Code's built-in `/code-review`).
- Not taken: upstream's `in-progress/` and `misc/` buckets.
- Do not edit these folders by hand. Update: `scripts/vendor.sh https://github.com/mattpocock/skills mattpocock-skills`
  then `scripts/install-vendor-skills.sh mattpocock-skills --skip code-review`.
- Drift check: `scripts/install-vendor-skills.sh mattpocock-skills --skip code-review --check`.

## License (MIT)

MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
