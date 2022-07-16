# core/section.py

import sys
from subprocess import run
from typing import Optional
from webbrowser import get

from mongoengine import Document, disconnect_all
from mongoengine.fields import IntField, ListField, StringField
from num2words import num2words
from pyparsing import str_type
from tqdm.auto import tqdm, trange
from alive_progress import alive_bar, alive_it
from yaml import dump_all

try:
    from core.atlas import BASE, max_title, sg
    from core.log import errwrap, log
    import core.book as book_
except ImportError:
    from atlas import BASE, max_title, sg
    from log import errwrap, log
    import book as book_

# .┌─────────────────────────────────────────────────────────────────┐.#
# .│                            Section                              │.#
# .└─────────────────────────────────────────────────────────────────┘.#

# >  Static Variables
BOOK_DIR = "/Users/maxludden/dev/py/superforge/books/"
img = (
    f'<figure>\n\t<img src="../Images/gem.gif" alt="gem" width="120" height="60" />\n  '
)


class InvalidPartException(Exception):
    pass


class SectionNotFound(Exception):
    pass


class MMDConversionException(Exception):
    pass


class MMDConversionError(Exception):
    pass


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

    def __int__(self):
        return self.section


@errwrap()  # . Verified
def get_book(section: int) -> int:
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


@errwrap()  # . Verified
def generate_part(section: int) -> int:
    """

    Determine the section Part number of its book (if it's books has more than one section.)

    Args:
        `section` (int):
            The section for which were are looking for.

    Returns:
        `part` (int):
            The given section's part number. If the given section's book contains only one section, `get_part()` will return `0`.
    """
    print(f"Section: {section}\nSelected Section Type: {type(section)}")
    part0 = [1, 2, 3]
    part1 = [4, 6, 8, 10, 12, 14, 16]
    part2 = [5, 7, 9, 11, 13, 15, 17]
    if section in part0:
        return 0
    elif section in part1:
        return 1
    elif section in part2:
        return 2
    else:
        raise InvalidPartException(f"Section {section} is not a valid section.")


def generate_part_word(section: int) -> str:
    """

    Generate the proper case of the spelled fersion od the partnu

    Args:
        `section` (int):
            The section for which were are looking for.

    Returns:
        `part` (int):
            The given section's part number. If the given section's book contains only one section, `get_part()` will return `0`.
    """
    print(f"Section: {section}\nSelected Section Type: {type(section)}")
    part0 = [1, 2, 3]
    part1 = [4, 6, 8, 10, 12, 14, 16]
    part2 = [5, 7, 9, 11, 13, 15, 17]
    if section in part0:
        return 0
    elif section in part1:
        return 1
    elif section in part2:
        return 2
    else:
        raise InvalidPartException(f"Section {section} is not a valid section.")


@errwrap()  # . Verified
def generate_title(section: int, save: bool = False):
    """
    Generate the title for the given section.

    Args:
        `section` (int):
            The given section
        `save` (bool, optional):
            Whether to save the title to MongoDB. Defaults to False.

    Returns:
        `title` (str):
            The title for the given section.
    """

    book = get_book(section)

    # > Get section's book from MongoDB
    sg()
    section_book = book_.Book.objects(book=book).first()
    title = section_book.title  # Get book title

    # > Part (if applicable)
    part = generate_part(section)
    if part == 2:
        title = f"{title} - Part 2"
    elif part == 1:
        title = f"{title} - Part 1"
    elif part == 0:
        title = f"{title}"
    else:
        raise InvalidPartException(f"Section {section} is not a valid section.")

    log.debug(f"Section {section}'s title: {title}")

    if save:
        sg()
        section_doc = Section.objects(section=section).first()
        if section_doc is None:
            raise SectionNotFound(f"Section {section} not found in MongoDB.")
        else:
            section_doc.title = title
            section_doc.save()
            log.debug(f"Saved title for Section {section}'s Section Page to MongoDB.")

    return title


@errwrap()
def get_title(section: int) -> str:
    sg()
    doc = Section.objects(section=section).first()
    return max_title(doc.title)


@errwrap()
def generate_filename(section: int) -> str:
    section = str(section).zfill(2)
    return f"section-{section}"


@errwrap()  # . Verified
def generate_md_path(section: int, save: bool = False) -> str:
    """Generate the md_path of the given section.

    Args:
        `section` (int):
            The given section.

    Returns:
        `md` (str):
            The filepath of the section's multimarkdown.
    """
    filename = generate_filename(section)
    book = get_book(section)
    book_str = str(book).zfill(2)
    book_dir = f"book{book_str}"
    md_path = f"{BASE}/books/{book_dir}/md/{filename}.md"
    if save:
        sg()
        section_page = Section.objects(section=section).first()
        if section_page is None:
            raise SectionNotFound(f"Section {section} not found.")
        else:
            section_page.md_path = md_path
            section_page.save()
            log.debug(f"Saved md_path for section {section} to MongoDB.")
    return md_path


@errwrap() # . Verified
def generate_html_path(section: int, save: bool = False) -> str:
    """
    Generate the html_path of the given section.

    Args:
        `section` (int):
            The given section.

    Returns:
        `md` (str):
            The filepath of the section's HTML.
    """
    filename = generate_filename(section)
    book = get_book(section)
    book_str = str(book).zfill(2)
    book_dir = f"book{book_str}"
    html_path = f"{BASE}/books/{book_str}/html/{filename}.html"
    if save:
        sg()
        section_page = Section.objects(section=section).first()
        if section_page is None:
            raise SectionNotFound(f"Section {section} not found.")
        else:
            section_page.html_path = html_path
            section_page.save()
            log.debug(f"Saved html_path for section {section} to MongoDB.")
    return html_path
    

@errwrap() # . Verified
def get_start(section: int) -> int:
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
    doc = Section.objects(section=section).first()
    return doc.start


@errwrap() # . Verified
def get_end(section: int) -> int:
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


@errwrap() # . Verified
def generate_md(section: int, save: bool = False, write: bool = False):
    """
    Generate the markdown for Section {section}'s Section Page.

    Args:
        `section` (int):
            The given section.
        `save` (bool):
            Whether to save the Section Page Markdown to MongoDB. Defualts to false.
        `write` (bool):
            Whether to write the Section Page's Markdown to Disk. Defualts to False.

    Returns:
        `md` (str):
            The markdown of the given section's Section Page.
    """
    sg()
    section_page = Section.objects(section=section).first()
    if section_page is None:
        raise SectionNotFound(f"Section {section} not found.")
    else:
        log.debug(f"Section {section} Document:<code>\n{section_page}\n</code>")
        title = section_page.title
        book = section_page.book
        book_word = str(num2words(book)).capitalize()
        start = section_page.start
        end = section_page.end
        md_path = section_page.md_path
        part = generate_part(section)

        # < Yaml Frontmatter Metadata
        meta = f"---\nTitle: {title}\nBook: {book}\nPart: {part}\nCSS: ../Styles/style.css\nviewport: width=device-width, initial-scale=1.0\n...\n  \n"

        # < Atx Heading
        atx = f'# {title}\n## Book {book_word}\n### Section {section}\n\n<figure>\n\t<img src="../Images/gem.gif" alt="Spinning Black Gem" width="120" height="60" />\n</figure>\n\n'

        # < Text
        text = f'<p class="title">Written by Twelve Winged Dark Seraphim</p>\n'
        text = f'{text}<p class="title">Compiled and Edited by Max Ludden</p>'

        md = f"{meta}{atx}{text}"

        if save:
            section_page.md = md
            section_page.save()
            log.info(f"Saved md for section {section} to MongoDB.")

        if write:
            with open(md_path, "w") as infile:
                infile.write(md)
                log.debug(f"Wrote md for section {section} to {md_path}.")

        return md


@errwrap() # . Verified
def get_md(section: int):
    """
    Retrieve the multimarkdown for the given section from MongoDB.

    Args:
        `section` (int):
            The given section.

    Returns:
        `md` (str):
            The multimarkdown for the given section.
    """
    sg()
    for doc in Section.objects(section=section):
        return doc.md


@errwrap()  #. Verified
def generate_html(section: int, save: bool = False):
    """
    Generate the given section's HTML from it's markdown.

    Args:
        `book` (int):
            The given book.

        `save` (bool, optional):
            Whether to save the HTML to MongoDB. Defaults to False.

    Returns:
        `html` (str):
            The HTML for the given section.
    """
    sg()
    section_page = Section.objects(section=section).first()
    if section_page is None:
        log.error(f"Section {section} not found in MongoDB.")
        raise SectionNotFound(
            f"MongoDB does not contain the following section: {section}."
        )
    else:
        md_path = section_page.md_path
        log.debug(f"Section {section}'s Markdown path:\n{md_path}")

        html_path = section_page.html_path
        log.debug(f"Section {section}'s HTML path:\n{html_path}")

        mmd_cmd = [
            "multimarkdown",
            "-f",
            "--nolabels",
            "-o",
            f"{section_page.html_path}",
            f"{section_page.md_path}",
        ]

        try:
            result = run(mmd_cmd)
            if result.returncode == 0:
                log.debug(f"Successfully generated HTML for Section {section}.")
        except MMDConversionException:
            raise MMDConversionError(
                f"Failed to generate Section {section}'s HTML.<code>\nmd_path: {md_path}\nhtml_path: {html_path}\nresult: {result}</code>"
            )
        else:
            with open(html_path, "r") as infile:
                generated_html = infile.read()
            html = generated_html.strip()

            if save:
                section_page.html = html
                section_page.save()
                log.debug(f"Saved Section {section}'s HTML to MongoDB.")

            return html


@errwrap() # . Verified
def generate_section_pages():
    sg()
    bar = alive_it(
        Section.objects(),
        bar="smooth",
        dual_line=True,
        title="Generateing Section Pages",
    )
    for section_doc in bar:
        section = section_doc.section

        bar.title(f"Generating Section {section}'s Section Page")

        bar.text(f"Generating Section {section} Page Markdown")
        md = generate_md(section, save=True, write=True)
        log.debug(f"Section {section} Markdown:\n<code>\n{md}</code>")

        bar.text(f"Generating Section Page HTML")

        html = generate_html(section, save=True)
        log.debug(f"Section {section} HTML:\n<code>\n{html}</code>")


@errwrap()
def generate_section_titles():
    sg()
    bar = alive_it(
        Section.objects(),
        bar="smooth",
        dual_line=True,
        title="Generating Section Titles",
    )
    for section_doc in bar:
        section = section_doc.section
        bar.title(f"Generating Section {section}'s Section Title")
        title = generate_title(section, save=True)
        bar.text(f"Section {section} Title: {title}")
        section_doc.title = title
        section_doc.save()
