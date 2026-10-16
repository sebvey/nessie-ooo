"""Check relative links in the project's Markdown files.

Prints each broken link and exits with status 1 if there is any. Links
inside fenced code blocks, URLs and pure anchors are skipped; the anchor
part of a link (#...) is not checked. The local ticket folder is skipped.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", "00-tracking"}
LINK = re.compile(r"\]\(([^)\s]+)\)")
FENCE = re.compile(r"```.*?```", re.S)


def broken_links():
    for folder, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if not name.endswith(".md"):
                continue
            path = os.path.join(folder, name)
            with open(path, encoding="utf-8") as f:
                text = FENCE.sub("", f.read())
            for target in LINK.findall(text):
                if re.match(r"^[a-z]+:", target) or target.startswith("#"):
                    continue
                target_path = target.split("#")[0]
                if not os.path.exists(os.path.normpath(os.path.join(folder, target_path))):
                    yield os.path.relpath(path, ROOT), target


def main():
    found = list(broken_links())
    for source, target in found:
        print(f"{source}: {target}")
    print(f"broken: {len(found)}")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
