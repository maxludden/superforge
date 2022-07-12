# core/section.py

import sys
from subprocess import run
from typing import Optional
from webbrowser import get

from mongoengine import Document, disconnect_all
from mongoengine.fields import IntField, ListField, StringField
from num2words import num2words
from tqdm.auto import tqdm

try:
    from core.atlas import BASE, max_title, sg
    from core.log import errwrap, log
except ImportError:
    from atlas import BASE, max_title, sg
    from log import errwrap, log

# .┌─────────────────────────────────────────────────────────────────┐.#
# .│                            Section                              │.#
# .└─────────────────────────────────────────────────────────────────┘.#

# >  Static Variables
BOOK_DIR = "/Users/maxludden/dev/py/superforge/books/"
img = (
    f'<figure>\n\t<img src="../Images/gem.gif" alt="gem" width="120" height="60" />\n  '
)


class Section(Document):
    section = IntField(min_value=1, max_value=17)
    title = StringField()
    book = IntField(min_value=1, max_value=10)
    chapters = ListField(IntField())
    start = IntField(min_value=1)
    end = IntField(max_value=3462)
    filename = StringField()
    mmd = StringField()
    mmd_path = StringField()
    md_path = StringField()
    md = StringField()
    html_path = StringField()
    html = StringField()
    section_files = ListField(StringField())


@errwrap()
def get_book(section: int):
    """Determine the book of a given chapter.

    Args:
        `section` (int):
            The given section.

    Returns:
        `book` (int):
            The book the given section is in.
    """
    book_sections = {
        1: 1,
        2: 2,
        3: 3,
        4: 4,
        5: 4,
        6: 5,
        7: 5,
        8: 6,
        9: 6,
        10: 7,
        11: 7,
        12: 8,
        13: 8,
        14: 9,
        15: 9,
        16: 10,
        17: 10,
    }
    book = book_sections[section]
    return book


@errwrap()
def get_title(section: int):
    sg()
    for doc in Section.objects(section=section):
        return max_title(doc.title)


@errwrap()
def get_part(section: int):
    """Determine the section Part number of its book (if it's books has more than one section.)

    Args:
        `section` (int):
            The section for which were are looking for.

    Returns:
        `part` (int):
            The given section's part number. If the given section's book contains only one section, `get_part()` will return `0`.
    """
    if section <= 3:
        return 0
    elif section % 2 == 0:
        return 1
    else:
        return 2


@errwrap()
def get_filename(section: int):
    section = str(section).zfill(2)
    return f"section-{section}"


@errwrap()
def get_md_path(section: int):
    """Generate the md_path of the given section.

    Args:
        `section` (int):
            The given section.

    Returns:
        `md` (str):
            The filepath of the section's multimarkdown.
    """
    filename = get_filename(section)
    book = str(get_book(section)).zfill(2)
    return f"/Users/maxludden/dev/py/superforge/books/book{book}/md/{filename}.md"


@errwrap()
def get_html_path(section: int):
    """
    Generate the html_path of the given section.

    Args:
        `section` (int):
            The given section.

    Returns:
        `md` (str):
            The filepath of the section's HTML.
    """
    filename = get_filename(section)
    book = str(get_book(section)).zfill(2)
    return f"/Users/maxludden/dev/py/superforge/books/book{book}/html/{filename}.html"


@errwrap()
def get_start(section: int):
    """
    Determine the chapter the sections starts at.

    Args:
        `section` (int):
            The given section.

    Returns:
        `start` (int):
            The chapter the given section begins.
    """
    sg()
    for doc in Section.objects(section=section):
        return doc.start


@errwrap()
def get_end(section: int):
    """
    Determine the chapter the section ends.

    Args:
        `section` (int):
            The given section.

    Returns:
        `end` (int):
            The chapter the given section ends.
    """
    sg()
    for doc in Section.objects(section=section):
        return doc.end


@errwrap(entry=False, exit=False)
def get_md(section: int):
    """
    Generate the multimarkdown for the given section and save it to disk and MongoDB

    Args:
        `section` (int):
            The given section.

    Returns:
        `md` (str):
            The multimarkdown for the given section.
    """
    sg()
    for doc in Section.objects(section=section):
        part = get_part(section)
        log.debug(f"Retrieved Section {section}'s Document from MongoDB.")
        book_word = str(num2words(doc.book)).title()

        # > Generate MD Metadata
        meta = f"Title: {doc.title}"
        meta = f"{meta}\nBook: {doc.book}"
        meta = f"{meta}\nSection: {doc.section}"

        if section > 3:
            meta = f"{meta}\nPart: {part}"

        meta = f"{meta}\nCSS:../Styles/style.css"
        meta = f"{meta}\nviewport: width=device-width\n  \n  "

        # . Declare img const
        img = '\n\n<figure>\n<img src="../Images/gem.gif" alt="gem" id="gem" width="120" height="60" />\n</figure>'

        if part == 0:

            atx = f"## Book {book_word}\n#### of Super Gene "
            atx = f"{atx}{img}\n\n### Chapter {doc.start} - Chapter {doc.end}\n<br>\n<br>\n<br>\n<br>"
        elif part == 1:
            atx = f"## Part One{img}\n  \n### Chapter {doc.start} - Chapter {doc.end}\n<br>\n<br>\n<br>\n<br>"
        else:
            atx = f"## Part Two{img}\n  \n### Chapter {doc.start} - Chapter {doc.end}\n<br>\n<br>\n<br>\n<br>\n<br>"

        text = '\n  \n<p class="title">Written by Twelve Winged Burning Seraphim</p>\n<p class="title">Compiled and edited by Max Ludden</p>\n'

        md = f"{meta}{atx}{text}"
        md_path = get_md_path(section)
        with open(md_path, "w") as outfile:
            outfile.write(md)
        log.debug(f"Wrote Sections {section}'s multimarkdown to disk.")
        doc.md = md
        doc.save()
        log.debug(f"Saved Section {section}'s multimarkdown to MongoDB.")
        return md


def get_html(section: int):
    """Generate the HTML for the given section.

    Args:
        `section` (int):
            The  given section.

    Returns:
        `html` (str):
            The HTML of the given section.
    """

    sg()
    for doc in Section.objects(section=section):
        md_path = get_md_path(doc.section)
        html_path = get_html_path(doc.section)
        md_cmd = ["multimarkdown", "-f", "--nolabels", "-o", html_path, md_path]
        log.debug(f"Multimarkdown Command:\n{md_cmd}")
        try:
            result = run(md_cmd, capture_output=True, text=True)
        except:
            write_html(section)
        else:
            book = str(get_book(doc.section)).zfill(2)
            zsection = str(doc.section).zfill(2)
            html_path = f"/Users/maxludden/dev/py/superforge/books/book{book}/html/section-{zsection}.html"
            with open(html_path, "r") as infile:
                html = infile.read()
            doc.html = html
            doc.save()
            log.debug("Saved Section {section}'s HTML to disk and MongoDB.")


def write_html(section: int, md: Optional[str]):
    if not md:
        connected = True
        sg()
        for doc in Section.objects(section=section):
            if doc.md == "":
                md = get_md(section)
    html = md(md, extras=["metadata"])
    with open(doc.html_path, "w") as outfile:
        outfile.write(html)

    if connected == True:
        disconnect_all()

    sg()
    for doc in Section.objects(section=section):
        doc.html = html
        doc.save()


@errwrap()
def make_sections():
    """A script to automate the generation of each section page's multimarkdown and convert it into X/HTML."""
    sg()
    sections = range(1, 18)
    for section in tqdm(sections, unit="section", desc="Writing section pages"):
        for doc in Section.objects(section=section):
            doc.filename = get_filename(doc.section)
            doc.md_path = get_md_path(doc.section)
            doc.md = get_md(doc.section)
            md = get_md(section)
            html = get_html(section)
            doc.md = md
            doc.html = html
            doc.save()
            log.info(f"Finished updating section {section}.md")


def save_html():
    """
    Read html from disk and save to MongoDB.
    """
    sg()
    for doc in tqdm(Section.objects(), unit="section", desc="Saving HTML"):
        doc.html_path = get_html_path(doc.section)
        with open(doc.html_path, "r") as infile:
            doc.html = infile.read()
        doc.save()
