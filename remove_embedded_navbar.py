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

page_lang_regex = re.compile(r"^(cursus_)?(?P<pageName>.*)_(?P<lang>EN|NL)$")

def main():
    regex = re.compile(r'<ul class="nav nav-tabs nav-centered".*?Contact.*?</ul>[ \t\n]*(?=.{,10}?<div)', re.DOTALL)
    for a in PAGES_DIR.glob("**/*.html"):
        with a.open("r", encoding="utf-8") as f:
             contents = f.read()
        m = regex.search(contents)
        if m is None:
            assert m

        new_contents = contents[:m.start()] + contents[m.end():]

        print(f"  In {PurePosixPath(a.relative_to(PAGES_DIR))}")
        # m = page_lang_regex.fullmatch(a.stem)

        # lang = m.group("lang").lower()

        # def subs_function(m):
        #     rel_path = PurePosixPath(m.group("relPath"))
        #     abs_path = to_abs(rel_path, base_path=a.parent / get_output_name(a), lang=lang)
        #     print(f"      {rel_path} -> {abs_path}")

        #     return f'href="{abs_path}"'


        # with a.open("r", encoding="utf-8") as f:
        #     contents = f.read()

        # # contents = (
        # #     contents
        # #     .replace('<a href="../">Home</a>', '<a href="/">Home</a>')
        # #     .replace('<a href="../../">Home</a>', '<a href="/">Home</a>')
        # #)
        # new_contents = regex.sub(subs_function, contents)

        with a.open("w", encoding="utf-8") as f:
            f.write(new_contents)

        print(f"Written {a}")

if __name__ == "__main__":
    main()





