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

container : Container = None

page_lang_regex = re.compile(r"^(?P<pageName>.*)_(?P<lang>EN|NL)$")


def main():
    global container

    container = Container.load(ROOT_DIR / "container.html")
    copy_assets()

    for a in PAGES_DIR.glob("**/*.html"):
        generate_page(a)


def copy_if_modified(src, dst):
    src_path = Path(src)
    dst_path = Path(dst)
    if (
        dst_path.exists() and
        src_path.stat().st_mtime == dst_path.stat().st_mtime
    ):
        return
    shutil.copy2(src, dst)

def copy_assets():
    shutil.copy2(ROOT_DIR / "index_redirect.html", DEST_DIR / "index.html")
    shutil.copytree(CSS_DIR, DEST_DIR / "css", dirs_exist_ok=True, copy_function=copy_if_modified)
    shutil.copytree(FONTS_DIR, DEST_DIR / "fonts", dirs_exist_ok=True, copy_function=copy_if_modified)

class Container:
    before: str
    after: str

    def __init__(self, before, after):
        self.before = before
        self.after = after

    @staticmethod
    def load(path: Path):
        with path.open("r", encoding="utf-8") as f:
            contents = f.read()

        [before, after] = contents.split("<!-- BODY -->")
        return Container(before, after)

    def apply(self, contents: str):
        return self.before + contents + self.after

GENERATE_LANGS = {"nl", "en"}

def generate_page(src_path: Path):
    name = src_path.stem
    langs = list(GENERATE_LANGS)

    src_modified = src_path.stat().st_mtime

    dst_suffix = {
        ".html": ".html"
    }[src_path.suffix]

    m = page_lang_regex.fullmatch(name)
    if m is not None:
        name = m.group("pageName")
        langs = []

        src_lang = m.group("lang").lower()
        for lang in GENERATE_LANGS:
            if lang == src_lang:
                langs.append(lang)
                continue

            # TODO Reimplement this mechanism
            expect_lang_path = src_path.parent / f"{name}_{lang.upper()}{src_path.suffix}"
            if not expect_lang_path.exists():
                print(f"  WARN: Mirroring {src_path.relative_to(PAGES_DIR)} from {src_lang} to {lang}!")
                langs.append(lang)

    if len(langs) == 0:
        return

    with src_path.open("r", encoding="utf-8") as f:
        src_contents = f.read()

    contents = container.apply(src_contents)

    dst_name = src_path.parent.relative_to(PAGES_DIR) / f"{name}{dst_suffix}"
    # if (src_path.parent / name).exists():
    if name != "index":
        dst_name = (src_path.parent / name / "index.html").relative_to(PAGES_DIR)
    dst_name = PurePosixPath(dst_name)

    # print(dst_name)

    for lang in langs:
        dst_path = (
            DEST_DIR / lang / dst_name
        )
        print(PurePosixPath(dst_path.relative_to(DEST_DIR)))

        dst_path.parent.mkdir(exist_ok=True,parents=True)

        if dst_path.exists():
            with dst_path.open("r", encoding="utf-8") as f:
                if f.read() == contents:
                    continue

        with dst_path.open("w", encoding="utf-8") as f:
            f.write(contents)

        print(f"  Written {PurePosixPath(dst_path.relative_to(ROOT_DIR))}")


if __name__ == "__main__":
    main()
