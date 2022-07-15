# core/section.py

import sys
from subprocess import run
from typing import Optional
from webbrowser import get

from mongoengine import Document, disconnect_all
from mongoengine.fields import IntField, ListField, StringField
from num2words import num2words
from pyparsing import str_type
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


@errwrap()
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


@errwrap()
def get_title(section: int) -> str:
    sg()
    for doc in Section.objects(section=section):
        return max_title(doc.title)


@errwrap()
def get_part(section: int) -> int:
    """Determine the section Part number of its book (if it's books has more than one section.)

    Args:
        `section` (int):
            The section for which were are looking for.

    Returns:
        `part` (int):
            The given section's part number. If the given section's book contains only one section, `get_part()` will return `0`.
    """
    section_type = type(section)
    log.info(f"Section type: {section_type}")
    if section <= 3:
        return 0
    elif section % 2 == 0:
        return 1
    else:
        return 2


@errwrap()
def get_filename(section: int) -> str:
    section = str(section).zfill(2)
    return f"section-{section}"


@errwrap()
def generate_md_path(section: int, save: bool = False) -> str:
    """Generate the md_path of the given section.

    Args:
        `section` (int):
            The given section.

    Returns:
        `md` (str):
            The filepath of the section's multimarkdown.
    """
    filename = get_filename(section)
    book_str = str(section).zfill(2)
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
            log.info(f"Saved md_path for section {section} to MongoDB.")
    return md_path


@errwrap()
def get_html_path(section: int) -> str:
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
    for doc in Section.objects(section=section):
        return doc.start


@errwrap()
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


@errwrap(entry=False, exit=False)
def generate_md(section: int, save: bool = False, write: bool = False) -> str:
    """
    Generate the multimarkdown for the given section and save it to disk and MongoDB

    Args:
        `section` (int):
            The given section.

    Returns:
        `md` (str):
            The multimarkdown for the given section.
    """
    part = get_part(section)
    sg()
    section_doc = Section.objects(section=section).first()
    book = section_doc.book
    book_word = section_doc.book_word
    title = section_doc.title
    start = section_doc.start
    end = section_doc.end
    

    # > Generate MD Metadata
    meta = f"---\nTitle: {title}\nBook: {book}\nSection: {section}"

    if section > 3:
        meta = f"{meta}\nPart: {part}"

    meta = f"{meta}\nCSS:../Styles/style.css\nviewport: width=device-width\n...\n  \n"

    # . Declare img const
    img = '\n\n<figure>\n<img src="../Images/gem.gif" alt="gem" id="gem" width="120" height="60" />\n</figure>'

    if part == 0:

        atx = f"## Book {book_word}\n#### of Super Gene "
        atx = f"{atx}{img}\n\n### Chapter {start} - Chapter {end}\n"
    elif part == 1:
        atx = f"## Part One{img}\n  \n### Chapter {start} - Chapter {end}\n"
    else:
        atx = f"## Part Two{img}\n### Chapter {start} - Chapter {end}\n"

    text = '\n<p class="title">Written by Twelve Winged Burning Seraphim</p>\n<p class="title">Compiled and edited by Max Ludden</p>\n'

    md = f"{meta}{atx}{text}"
    
    if write:
        md_path = generate_md_path(section)
        with open(md_path, "w") as outfile:
            outfile.write(md)
        log.debug(f"Wrote Sections {section}'s multimarkdown to disk.")
    
    if save:
        section_doc.md = md
        section_doc.save()
        log.debug(f"Saved Section {section}'s multimarkdown to MongoDB.")
    return md


@errwrap()
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
        
        
@errwrap()
def generate_html(section: int, save: bool = False):
    '''
    Generate the given section's HTML from it's markdown.
    
    Args:
        `book` (int):
            The given book.
            
        `save` (bool, optional):
            Whether to save the HTML to MongoDB. Defaults to False.
            
    Returns:
        `html` (str):
            The HTML for the given section.
    '''
    sg()
    section_page = Section.objects(section=section).first()
    if section_page is None:
        log.error(f"Section {section} not found in MongoDB.")
        raise SectionNotFound(f"MongoDB does not contain the following section: {section}.")
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
            f"{section_page.md_path}"
        ]
        
        try:
            result = run(mmd_cmd)
            if result.returncode == 0:
                log.debug(f"Successfully generated HTML for Section {section}.")
        except MMDConversionException:
            raise MMDConversionError(f"Failed to generate Section {section}'s HTML.<code>\nmd_path: {md_path}\nhtml_path: {html_path}\nresult: {result}</code>")
        else:
            with open (html_path, 'r') as infile:
                html = infile.read()
            
            if save:
                section_page.html = html
                section_page.save()
                log.debug(f"Saved Section {section}'s HTML to MongoDB.")
            
            return html


sg()
for section in tqdm(Section.objects(), unit="sections", desc="Generating Section Pages"):
    md = generate_md(section, save=True, write=True)
    log.info(md)

    html = generate_html(1, save=True)
    log.info(html)
            
        
        
        