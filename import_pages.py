from __future__ import annotations

from pathlib import Path, PurePosixPath
import shutil
import re
import navigation_bar

# Copyright (c) 2022 Vincent Kuhlmann

# This script generates all of the files for the website in the output directory.


# Define the locations of all of the files 
ROOT_DIR = Path.cwd()
CSS_DIR = ROOT_DIR / "css"
FONTS_DIR = ROOT_DIR / "fonts"
ASSETS_DIR = ROOT_DIR / "assets"
JAVASCRIPT_DIR = ROOT_DIR / "js"

SRC_DIR = ROOT_DIR / "src"
PAGES_DIR = ROOT_DIR / "src" / "pages"

# Define the location for the output and check that it exists
DEST_DIR = Path.cwd() / ".." / "texnicie-www-gh-pages"
assert DEST_DIR.exists()

container : Container = None

# This defines how to look for specific strings or patterns
page_lang_regex = re.compile(r"^(?P<dirRepeat>cursus_)?(?P<pageName>.*)_(?P<lang>EN|NL)$")

page_title_regex = re.compile(r"<!-- PAGE_TITLE: (?P<pageTitle>((?!-->).)*) -->")

cursus_year_regex = re.compile(r"^(?P<year>\d{4}-\d{4})$")

# Function finds all of the years, used for making the links to the cursus page of each year
def get_cursus_years() -> list[str]:
    cursus_dir = PAGES_DIR / "cursus"

    years = set()

    for path in cursus_dir.glob("*.html"):
        m = re.fullmatch(
            r"(?:cursus_)?(?P<year>\d{4}-\d{4})_(NL|EN)\.html",
            path.name
        )
        if m:
            years.add(m.group("year"))

    return sorted(years, reverse=True)

def generate_cursus_year_navigation(current_year, language):
    years = get_cursus_years()

    result = []

    for year in years:
        if year == current_year:
            result.append(
                f'''
                <li class="active">
                    <a href="#">{
                        year
                    }</a>
                </li>
                '''
            )
        else:
            prefix = "" if language == "nl" else "/en"

            result.append(
                f'''
                <li style="background-color:hsl(208, 56%, 95%);">
                    <a href="{prefix}/cursus/{year}">
                        {year}
                    </a>
                </li>
                '''
            )
    return "\n".join(result)

def import_cursus_years(contents, current_year, language):
    navigation = generate_cursus_year_navigation(
        current_year,
        language
    )

    return contents.replace(
        "<!-- IMPORT_CURSUS_YEARS -->",
        navigation
    )

def create_cursus_redirect(language):
    years = get_cursus_years()

    if not years:
        raise Exception("No cursus years found")

    newest_year = years[0]

    if language == "nl":
        url = f"/cursus/{newest_year}"
    else:
        url = f"/en/cursus/{newest_year}"

    return f"""<!DOCTYPE html>
<html lang="{language}">
<head>
    <meta http-equiv="refresh" content="0; url={url}">
    <link rel="canonical" href="https://texnicie.nl{url}">
</head>
<body>
    <p><a href="{url}">Redirecting...</a></p>
</body>
</html>
"""


# Extract the pagename out of the name of the html document, e.g. cursus_2024-2025_NL -> 2024-2025
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

    for page in PAGES_DIR.glob("**/*.html"):
        if ".fragment" in page.suffixes:
            continue
        generate_page(src_path=page)


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
    (DEST_DIR / "en").mkdir(exist_ok=True)
    with (DEST_DIR / "cursus.html").open("w", encoding="utf-8") as f:
        f.write(create_cursus_redirect("nl"))
    with (DEST_DIR / "en" / "cursus.html").open("w", encoding="utf-8") as f:
        f.write(create_cursus_redirect("en"))
    shutil.copytree(ASSETS_DIR, DEST_DIR / "assets", dirs_exist_ok=True, copy_function=copy_if_modified)
    shutil.copytree(CSS_DIR, DEST_DIR / "css", dirs_exist_ok=True, copy_function=copy_if_modified)
    shutil.copytree(FONTS_DIR, DEST_DIR / "fonts", dirs_exist_ok=True, copy_function=copy_if_modified)
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
        rel_path = PurePosixPath(fragment_name).relative_to("/")
        source = PAGES_DIR / rel_path
        if not source.exists() and rel_path.parts[0].startswith("20"):
            source = SRC_DIR / rel_path

        if not source.exists():
            raise Exception(f"Cannot find fragment {fragment_name}")
        with source.open("r", encoding="utf-8") as f:
            fragment = f.read()
        return fragment

    contents = re.sub(
        r"<!-- IMPORT (?P<fragmentName>[/a-zA-Z0-9._-]+) *-->",
        replacer, contents
    )
    return contents


def import_scripts(contents):
    scripts = list(re.finditer(r"<!-- IMPORT_SCRIPT (?P<scriptName>[/a-zA-Z0-9._-]+) *-->", contents))

    scriptNames = sorted(list({
        m.group("scriptName") for m in scripts
    }))

    scriptImports = "\n".join([
        f'<script src="{scriptName}"></script>\n'
        for scriptName in scriptNames
    ])

    print(scriptImports)

    m = re.search("<!-- HEAD INSERT SCRIPTS -->", contents)
    if m is None:
        raise Exception("Could not find insert point of scripts")

    contents = contents[:m.start(0)] + scriptImports + contents[m.end(0):]

    # contents = re.sub(
    #     r"<!-- IMPORT (?P<fragmentName>[a-zA-Z0-9._-]+) *-->",
    #     replacer, contents
    # )
    return contents

def import_styles(contents):
    styles = list(re.finditer(r"<!-- IMPORT_STYLE (?P<styleName>[/a-zA-Z0-9._-]+) *-->", contents))

    styleNames = sorted(list({
        m.group("styleName") for m in styles
    }))

    styleImports = "\n".join([
        f'<link href="{styleName}" rel="stylesheet" type="text/css">\n'
        for styleName in styleNames
    ])

    #print(styleImports)

    m = re.search("<!-- HEAD INSERT STYLE -->", contents)
    if m is None:
        raise Exception("Could not find insert point of styles")

    contents = contents[:m.start(0)] + styleImports + contents[m.end(0):]

    # contents = re.sub(
    #     r"<!-- IMPORT (?P<fragmentName>[a-zA-Z0-9._-]+) *-->",
    #     replacer, contents
    # )
    return contents


def generate_page(src_path: Path):
    name = src_path.stem
    langs = list(GENERATE_LANGS)

    current_year = None

    if src_path.parent.name == "cursus":
        m = re.fullmatch(
            r"(?:cursus_)?(?P<year>\d{4}-\d{4})_(NL|EN)",
            name
        )
        if m:
            current_year = m.group("year")

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
        if len(path.parts) == 0:
            with_slash = True
        #with_slash = True

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

        if current_year is not None:
            contents = import_cursus_years(
                contents,
                current_year,
                lang
            )
        contents = import_scripts(contents)
        contents = import_styles(contents)

        if dst_path.exists():
            with dst_path.open("r", encoding="utf-8") as f:
                if f.read() == contents:
                    continue

        with dst_path.open("w", encoding="utf-8") as f:
            f.write(contents)

        print(f"  Written {PurePosixPath(dst_path.relative_to(ROOT_DIR))}")


if __name__ == "__main__":
    main()



