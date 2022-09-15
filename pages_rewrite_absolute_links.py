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

def get_output_name(a: PurePosixPath) -> str:
    m = page_lang_regex.fullmatch(a.stem)
    if m is not None:
        return m.group("pageName")

    return a.name


def to_abs(path: PurePosixPath, base_path: Path, lang: str) -> PurePosixPath:
    first_part_index = next(
        i for i, part in enumerate(path.parts)
        if part not in {".", ".."}
    )
    rel_stripped = PurePosixPath(*path.parts[first_part_index:])

    attempt_paths = itertools.chain(
        [(base_path / path).resolve()],
        (
            parent / rel_stripped
            for parent in itertools.chain([base_path], base_path.parents)
        )
    )

    abs_path = None

    for attempt_path in attempt_paths:
        if (
            not attempt_path.parent.exists()
            or
            not attempt_path.resolve().parent.is_relative_to(PAGES_DIR)
        ):
            continue

        if attempt_path.exists():
            abs_path = attempt_path
            break

        contents = (
            get_output_name(a)
            for a in attempt_path.parent.iterdir()
        )

        found = False
        for content_name in contents:
            if content_name == attempt_path.name:
                found = True
                break
        
        if found:
            abs_path = attempt_path
            break

    if abs_path is None:
        print(f"WARN: Could not find absolute path for {path} with base_path {base_path}")
        return path

    abs_path = abs_path.relative_to(PAGES_DIR)

    if lang not in {"nl"}:
        abs_path = PurePosixPath(f"/{lang}") / abs_path

    abs_path = PurePosixPath("/") / abs_path

    return abs_path

def main():
    regex = re.compile(r'href *= *"(?P<relPath>(\./|\.\./)+[^"]+)"')
    for a in PAGES_DIR.glob("**/*.html"):
        print(f"In {PurePosixPath(a.relative_to(PAGES_DIR))}")
        m = page_lang_regex.fullmatch(a.stem)

        lang = m.group("lang").lower()

        def subs_function(m):
            rel_path = PurePosixPath(m.group("relPath"))
            abs_path = to_abs(rel_path, base_path=a.parent, lang=lang)
            print(f"  {rel_path} -> {abs_path}")

            return f'href="{abs_path}"'


        with a.open("r", encoding="utf-8") as f:
            contents = f.read()
        new_contents = regex.sub(subs_function, contents)

        # with a.open("w", encoding="utf-8") as f:
        #     f.write(new_contents)

        # print(f"Written {a}")
        # return

if __name__ == "__main__":
    main()



