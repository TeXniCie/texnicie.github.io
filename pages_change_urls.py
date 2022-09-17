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

def main():
    regex = re.compile(r'href *= *"(?P<path>/[^":]*)"')
    for a in PAGES_DIR.glob("**/*.html"):
        print(f"  In {PurePosixPath(a.relative_to(PAGES_DIR))}")

        def subs_function(m):
            path = m.group("path")
            #print(path)

            new_path = path
            # if path == "/":
            #     new_path = "/installatie"
            # if path == "/en/" or path == "/en":
            #     new_path = "/en/installatie"

            # if path == "/cursus":
            #     new_path = "/"
            # if path == "/en/cursus":
            #     new_path = "/en/"

            if path != new_path:
                print(f"      {path} -> {new_path}")

            return f'href="{new_path}"'


        with a.open("r", encoding="utf-8") as f:
            contents = f.read()

        # contents = (
        #     contents
        #     .replace('<a href="../">Home</a>', '<a href="/">Home</a>')
        #     .replace('<a href="../../">Home</a>', '<a href="/">Home</a>')
        #)
        new_contents = regex.sub(subs_function, contents)

        # with a.open("w", encoding="utf-8") as f:
        #     f.write(new_contents)

        # print(f"Written {a}")

if __name__ == "__main__":
    main()



