from __future__ import annotations

from pathlib import Path, PurePosixPath
import shutil
import re
import navigation_bar

# Copyright (c) 2022 Vincent Kuhlmann

ROOT_DIR = Path.cwd()
CSS_DIR = ROOT_DIR / "css"
FONTS_DIR = ROOT_DIR / "fonts"
DOWNLOADS_DIR = ROOT_DIR / "downloads"
ASSETS_DIR = ROOT_DIR / "assets"
JAVASCRIPT_DIR = ROOT_DIR / "js"

PAGES_DIR = ROOT_DIR / "src" / "pages"
DEST_DIR = Path.cwd() / ".." / "texnicie-www-gh-pages"

assert DEST_DIR.exists()

container : Container = None

page_lang_regex = re.compile(r"^(?P<dirRepeat>cursus_)?(?P<pageName>.*)_(?P<lang>EN|NL)$")

page_title_regex = re.compile(r"<!-- PAGE_TITLE: (?P<pageTitle>((?!-->).)*) -->")

def get_output_name(a: PurePosixPath) -> str:
    m = page_lang_regex.fullmatch(a.stem)
    if m is not None:
        return m.group("pageName")

    return a.name

def main():
    global container

    DEST_DIR.mkdir(exist_ok=True)
    (DEST_DIR / ".nojekyll").touch()

    container = Container.load(ROOT_DIR / "container.html")
    copy_assets()

    for a in PAGES_DIR.glob("**/*.html"):
        if ".fragment" in a.suffixes:
            continue
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
    #shutil.copy2(ROOT_DIR / "index_redirect.html", DEST_DIR / "index.html")
    shutil.copy2(ROOT_DIR / "cursusRedirect.html", DEST_DIR / "cursus.html")
    shutil.copy2(ROOT_DIR / "cursusRedirect.html", DEST_DIR / "en" / "cursus.html")
    shutil.copytree(ASSETS_DIR, DEST_DIR / "assets", dirs_exist_ok=True, copy_function=copy_if_modified)
    shutil.copytree(CSS_DIR, DEST_DIR / "css", dirs_exist_ok=True, copy_function=copy_if_modified)
    shutil.copytree(FONTS_DIR, DEST_DIR / "fonts", dirs_exist_ok=True, copy_function=copy_if_modified)
    shutil.copytree(DOWNLOADS_DIR, DEST_DIR / "downloads", dirs_exist_ok=True, copy_function=copy_if_modified)
    shutil.copytree(JAVASCRIPT_DIR, DEST_DIR / "js", dirs_exist_ok=True, copy_function=copy_if_modified)

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

    def apply(self, contents: str, lang: str = "en"):
        m = page_title_regex.search(contents)
        page_title = None
        if m is not None:
            page_title = f"{m.group('pageTitle')} | TeXniCie"

        if page_title is None:
            page_title = "TeXniCie"

        before = (
            self.before
            .replace('<html lang="en" ', f'<html lang="{lang}" ')
            .replace('<!-- PAGE_TITLE -->', page_title)
        )
        
        return before + contents + self.after

GENERATE_LANGS = {"nl", "en"}

def fill_fragments(contents):
    def replacer(m):
        fragment_name = m.group("fragmentName")
        source = PAGES_DIR / fragment_name
        if not source.exists():
            raise Exception(f"Cannot find fragment {fragment_name}")
        with source.open("r", encoding="utf-8") as f:
            fragment = f.read()
        return fragment

    contents = re.sub(
        r"<!-- IMPORT (?P<fragmentName>[a-zA-Z0-9._-]+) *-->",
        replacer, contents
    )
    return contents

def generate_page(src_path: Path):
    name = src_path.stem
    langs = list(GENERATE_LANGS)

    src_modified = src_path.stat().st_mtime

    dst_suffix = {
        ".html": ".html"
    }[src_path.suffix]

    src_lang = "en"

    m = page_lang_regex.fullmatch(name)
    if m is not None:
        name = m.group("pageName")
        langs = []

        src_lang = m.group("lang").lower()
        for lang in GENERATE_LANGS:
            if lang == src_lang:
                langs.append(lang)
                continue

        #     for a in src_path.parent.iterdir():
        #         if get_output_name(a) == name:
        #                 contents = (
        #     get_output_name(a)
        #     for a in attempt_path.parent.iterdir()
        # )


            # TODO Reimplement this mechanism
            expect_lang_path = src_path.parent / f"{m.group('dirRepeat') or ''}{name}_{lang.upper()}{src_path.suffix}"
            if not expect_lang_path.exists():
                print(f"  WARN: Mirroring {src_path.relative_to(PAGES_DIR)} from {src_lang} to {lang}!")
                langs.append(lang)

    if len(langs) == 0:
        return

    with src_path.open("r", encoding="utf-8") as f:
        src_contents = f.read()

    # dst_name = src_path.parent.relative_to(PAGES_DIR) / f"{name}{dst_suffix}"
    path = src_path.parent.relative_to(PAGES_DIR) / f"{name}"
    path = PurePosixPath(path)
    with_slash = False
    if path.name == "index":
        path = path.parent
        with_slash = True

    dst_name = src_path.parent.relative_to(PAGES_DIR) / f"{name}"

    # if (src_path.parent / name).exists():
    # if name != "index":
    #     dst_name = (src_path.parent / name / "index.html").relative_to(PAGES_DIR)
    dst_name = PurePosixPath(dst_name)

    # print(dst_name)

    for lang in langs:
        lang_prefix = PurePosixPath("/") / lang
        if lang == "nl":
            lang_prefix = PurePosixPath("/")

        url_path = lang_prefix / dst_name
        localized_path = lang_prefix / path

        print(localized_path)
        dst_path = DEST_DIR / url_path.relative_to("/")
        dst_path = dst_path.parent / f"{dst_path.name}{dst_suffix}"

        dst_path.parent.mkdir(exist_ok=True,parents=True)

        navbar = navigation_bar.create_for(str(localized_path).removesuffix("/") + ("/" if with_slash else ""), lang)
        contents = navbar + src_contents

        contents = container.apply(contents, lang=src_lang)

        subs_count = 0
        prev_contents = None
        while prev_contents != contents:
            if subs_count >= 10:
                print("!!! Stopping fragment recursion after 10 iterations!")
                break

            prev_contents = contents
            contents = fill_fragments(contents)

            subs_count += 1

        if dst_path.exists():
            with dst_path.open("r", encoding="utf-8") as f:
                if f.read() == contents:
                    continue

        with dst_path.open("w", encoding="utf-8") as f:
            f.write(contents)

        print(f"  Written {PurePosixPath(dst_path.relative_to(ROOT_DIR))}")


if __name__ == "__main__":
    main()
