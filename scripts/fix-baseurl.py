#!/usr/bin/env python3
"""Rewrite root-relative links in Jekyll's built output for project Pages.

brightmann/mbgi is served at https://brightmann.github.io/mbgi/, but post
content (183 posts) links images and other posts with root paths like
/images/... and /2019/05/27/.... On the /mbgi/ subpath those escape the
site and 404. Layout chrome is already baseurl-aware via `relative_url`;
this script fixes everything else, in the built HTML/XML/CSS only, so no
source post is ever touched.

Rule: for href/src/action attributes (and CSS url(...)) that start with a
single slash, prefix /mbgi — unless already prefixed. Protocol-relative
(//...), absolute (http...), anchor (#...), mailto:, data: and similar
values never start with a single slash, so they are untouched by design.
Code samples are escaped text in the built HTML (&lt;a href=...), not
real attributes, so they are untouched too. Idempotent: safe to re-run.
"""

import re
import sys
from pathlib import Path

BASE = "/mbgi"

ATTR_RE = re.compile(r'((?:href|src|action)=["\'])/(?!/)(?!mbgi/)([^"\']*)')
CSS_RE = re.compile(r'(url\(["\']?)/(?!/)(?!mbgi/)([^)"\']*)')


def fix_text(text: str) -> str:
    text = ATTR_RE.sub(r'\1' + BASE + r'/\2', text)
    text = CSS_RE.sub(r'\1' + BASE + r'/\2', text)
    return text


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("public")
    changed = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in (".html", ".xml", ".css"):
            continue
        original = path.read_text(encoding="utf-8", errors="ignore")
        fixed = fix_text(original)
        if fixed != original:
            path.write_text(fixed, encoding="utf-8")
            changed += 1
    print(f"fix-baseurl: rewrote {changed} files under {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
