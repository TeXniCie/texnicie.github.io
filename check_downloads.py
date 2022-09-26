from __future__ import annotations

from pathlib import Path, PurePosixPath
import shutil
import re
import itertools

# Copyright (c) 2022 Vincent Kuhlmann

ROOT_DIR = Path.cwd()
CSS_DIR = ROOT_DIR / "css"
FONTS_DIR = ROOT_DIR / "fonts"

PAGES_DIR = ROOT_DIR / "src" / "pages"
DEST_DIR = ROOT_DIR / "build"

downloads_source = Path.cwd().parent / "texnicie-www-downloads"

assert downloads_source.exists()

def main():
    # regex = re.compile(r'"(?P<downloadPath>/downloads/[^"]+)')
    regex = re.compile(r'"(?P<downloadPath>[^"]+(\.tex|\.pdf)|/downloads/[^"]+)"')
    for a in PAGES_DIR.glob("**/*.html"):
        print(f"In {PurePosixPath(a.relative_to(PAGES_DIR))}")

        with a.open("r", encoding="utf-8") as f:
            contents = f.read()

        for m in regex.finditer(contents):
            online_path = PurePosixPath(m.group("downloadPath"))
            if not online_path.is_relative_to("/downloads"):
                print(f"Not on downloads path: {online_path}")
                continue

            local_path = downloads_source / online_path.relative_to("/downloads")

            if not local_path.exists():
                print(f"    {online_path}")
        
        #regex.match(a)


if __name__ == "__main__":
    main()



