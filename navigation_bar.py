from __future__ import annotations

import re
from pathlib import PurePosixPath
import html
from typing import Union

class NavButton:
    def __init__(self, name, url):
        self.name = name
        self.url = PurePosixPath(url)
    
    def includes(self, url):
        return (PurePosixPath("/") / url).is_relative_to(self.url)

    def toHTML(self, is_active) -> str:
        return f'''
            <li {'class="active"' if is_active else ""} style="float:none;display:inline-block;">
                <a href="{str(self.url) if not is_active or True else "#"}">{html.escape(self.name)}</a>
            </li>
        '''

class NavButtonDropDown:
    main: NavButton
    children: list[NavButton]

    def __init__(self, name, url, children):
        self.main = NavButton(name, url)
        # self.name = name
        # self.dest = PurePosixPath(dest)
        self.children = list(children)

    def includes(self, url):
        return self.main.includes(url)

    @property
    def url(self):
        return self.main.url

    @property
    def name(self):
        return self.main.name
    
    def toHTML(self, is_active) -> str:
        return f'''
            <li class="dropdown {"active" if is_active else ""}" style="float:none;display:inline-block;">
                <a class="dropdown-toggle" href="{html.escape(str(self.main.url))}">
                    {html.escape(self.main.name)}
                    <!-- <span class="caret"></span> -->
                </a>
                <ul class="dropdown-menu">
                    {"".join(
                        f"""
                        <li>
                            <a href="{html.escape(str(child.url))}">{html.escape(child.name)}</a>
                        </li>
                        """
                        for child in self.children
                    )}
                </ul>
            </li>
        '''

# class LocalPath(PurePosixPath):
#     #path: PurePosixPath

#     def __init__(self, path, prefix=None):
#         m = re.fullmatch(r"(/(?!/)[a-zA-Z0-9_.-]+)*", path)
#         assert m

#         self.prefix = prefix

#         #self.path = PurePosixPath(path)
#         super().__init__(path)

#     def website_url(self):
#         return html.escape()


def create_for(dest_url: str, language: str):
    #m = re.fullmatch(r"/([a-zA-Z0-9_.-]+(/(?!$)|$))*$", dest_url)
    m = re.fullmatch(r"/([a-zA-Z0-9_.-]+(/|$))*$", dest_url)
    assert m is not None

    parts = tuple(dest_url.lstrip("/").split("/"))
    path = PurePosixPath(dest_url)

    # assert dest_url.startswith("/")
    #canonical_url = f"texnicie.nl/{dest_url.lstrip('/')}".rstrip("/")
    canonical_url = f"texnicie.nl/{dest_url.lstrip('/')}" if dest_url != "/" else "texnicie.nl"

    assert language in {"nl", "en"}
    prefix = f"/{language}" if language != "nl" else ""

    def url(val):
        return prefix + val

    # transl = {
    #     "Overzicht": "Overview",
    #     "Installatie": "Installation"
    # }

    def loc(t, en):
        if language == "en":
            #return transl.get(t, t)
            return en
        return t

    destinations: list[Union[NavButton, NavButtonDropDown]] = [
        NavButton("Home", url("/")),
        NavButtonDropDown("A-Es templates", url("/aes-templates"),
            [
                NavButton(loc("Gebruik", "Usage"), url("/aes-templates")),
                NavButton(loc("Installatie", "Installation"), url("/aes-templates/installatie"))
            ]
        ),
        # NavButton(loc("Cursus", "Course"), url("/cursus")),
        NavButton(loc("Installatie", "Installation"), url("/installatie")),
        NavButton(loc("Cursussen", "Courses"), url("/cursus")),
        NavButton("Contact", url("/contact"))
    ]

    def get_dest_score(dest : Union[NavButton, NavButtonDropDown]):
        if dest is None:
            return 0
        
        if len(dest.url.parts) > len(path.parts):
            return -1
        
        if (
            path.parts[:len(dest.url.parts)] == dest.url.parts
            and 
            (dest.url != PurePosixPath(url("/")) or path == PurePosixPath(url("/")))
        ):
            return len(dest.url.parts)

        return -1

    active_dest = max(
        [*destinations, None]
    , key=get_dest_score)

    return f'''
        <div class="navbar-header;" style="position:absolute;left:0px;max-width:0px;
            max-width:calc(100% - min(max(calc((50em - 100%) * 10000), 0px), 100%));
            overflow-x:hidden;">
            <div style="display:inline-block;width:50em;"><a class="navbar-brand" href="https://{canonical_url}"
                    style="color:#555;cursor:default;">{canonical_url} </a></div>
        </div>

        <ul class="nav nav-tabs nav-centered" style="text-align:center;">
            {
                "".join(
                    dest.toHTML(dest == active_dest)
                    for dest in destinations
                )
            }
        </ul>
    '''
