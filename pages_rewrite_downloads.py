from __future__ import annotations

from pathlib import Path, PurePosixPath
import shutil
import re

# Copyright (c) 2022 Vincent Kuhlmann

ROOT_DIR = Path.cwd()
CSS_DIR = ROOT_DIR / "css"
FONTS_DIR = ROOT_DIR / "fonts"

PAGES_DIR = ROOT_DIR / "src" / "pages"
DEST_DIR = ROOT_DIR / "build"

def main():
    regex = re.compile(r'href *= *"(\./|\.\./)*downloads/')
    for a in PAGES_DIR.glob("**/*.html"):
        with a.open("r", encoding="utf-8") as f:
            contents = f.read()
        new_contents = regex.sub(lambda m: f'href="/downloads/', contents)

        with a.open("w", encoding="utf-8") as f:
            f.write(new_contents)

        print(f"Written {a}")
        # return

if __name__ == "__main__":
    main()

