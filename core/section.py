# core/section.py

import sys
from cgitb import html
from enum import unique
from mailbox import MMDF
from subprocess import run

from mongoengine import Document
from mongoengine.fields import IntField, ListField, StringField
from num2words import num2words

from core.atlas import max_title, sg
from core.log import errwrap, log

#.##########################################################
#.                                                         #
#.                           d8   ,e,                      #
#.   dP"Y  ,e e,   e88'888  d88    "   e88 88e  888 8e     #
#.  C88b  d88 88b d888  '8 d88888 888 d888 888b 888 88b    #
#.   Y88D 888   , Y888   ,  888   888 Y888 888P 888 888    #
#.  d,dP   "YeeP"  "88,e8'  888   888  "88 88"  888 888    #
#.                                                         #
#.                                                         #
#.##########################################################

class Section(Document):
    section = IntField(unique=True)
    title = StringField()
    book = IntField(),
    chapters = ListField(IntField(unique=True))
    start = IntField()
    end = IntField()
    filename = StringField()
    mmd_path = StringField()
    mmd = StringField()
    html_path = StringField()
    html = StringField()

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
    try:
        if section == 1:
            return 1
        elif section == 2:
            return 2
        elif section == 3:
            return 3
        elif section == 4 | section == 5:
            return 4
        elif section == 6 | section == 7:
            return 5
        elif section == 8 | section == 9:
            return 6
        elif section == 10 | section == 11:
            return 7
        elif section == 12 | section == 13:
            return 8
        elif section == 14 | section == 15:
            return 9
        elif section == 16 | section == 17:
            return 10
        else:
            raise ValueError("Invalid section: {section}")
            sys.exit(
                {
                    "-3": {
                        "error": "Invalid Input Error",
                        "function": "chapter.get_book",
                        "chapter": chapter,
                    }
                }
            )
    except:
        raise ValueError("Invalid Section: {section}")


@errwrap()
def get_title(section: int):
    sg()
    for doc in Section.objects(section=section):
        return max_title(doc.title)

@errwrap()
def get_filename(section: int):
    section = str(section).zfill(2)
    return f'section-{section}'


@errwrap()
def get_mmd_path(section: int):
    """Generate the mmd_path of the given section.

    Args:
        `section` (int): 
            The given section.

    Returns:
        `mmd` (str): 
            The filepath of the section's multimarkdown.
    """
    filename = get_filename(section)
    book = str(get_book(section)).zfill(2)
    return f"/Users/maxludden/dev/py/superforge/books/book{book}/mmd/{filename}.mmd"

@errwrap()
def get_html_path(section: int):
    """Generate the html_path of the given section.

    Args:
        `section` (int): 
            The given section.

    Returns:
        `mmd` (str): 
            The filepath of the section's HTML.
    """
    filename = get_filename(section)
    book = str(get_book(section)).zfill(2)
    return f"/Users/maxludden/dev/py/superforge/books/book{book}/html/{filename}.html"

@errwrap()
def get_start(section: int):
    """Determine the chapter the sections starts at.

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
    """Determine the chapter the section ends.

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
    sg()
    sections = []
    for doc in Section.objects(book=doc.book):
        sections.append(doc.section)
    if len(sections) > 1:
        part1 = min(sections)
        if part1 == section:
            return 1
        else:
            return 2
    else:
        return 0
    
def get_mmd(section: int):
    """Generate the multimarkdown for the given section and save it to disk and MongoDB

    Args:
        `section` (int):
            The given section.

    Returns:
        `mmd` (str):
            The multimarkdown for the given section.
    """
    sg()
    for doc in Section.objects(section=section):
        part = get_part(section)
        
        meta = f'Title: {doc.title}'
        meta = f'{meta}\nSection: {doc.section}'
        meta = f'{meta}\nPart: {part}'
        meta = f'{meta}CSS:../Styles/style.css'
        meta = f'{meta}viewport: width=device-width\n\n'
        
        img = '\n\n<figure>\n<img src="../Images/gem.gif" alt="gem" id="gem" width="120" height="60" />\n\n</figure>'
        if part == 0:
            book_word = str(num2words(doc.book)).title()
            atx = f'## Book {book_word} of Super Gene'
            atx = f'{atx}{img}\n\n### Chapter {doc.start} - Chapter {doc.end}\n'
        elif part == 1:
            atx = f'## Part One{img}\n\n### Chapter {doc.start} - Chapter {doc.end}\n'
        else:
            atx = f'## Part Two{img}\n\n### Chapter {doc.start} - Chapter {doc.end}\n'
            
        text = '\n\n#### Written by Twelve Winged Burning Seraphim\n#### Compiled and edited by Max Ludden.\n'
        
        mmd = f'{meta}{atx}{text}'
        mmd_path = get_mmd_path(section)
        with open (mmd_path, 'w') as outfile:
            outfile.write(mmd)
        log.debug(f"Wrote Sections {section}'s multimarkdown to disk.")
        doc.mmd = mmd
        doc.save()
        log.debug(f"Saved Section {section}'s multimarkdown to MongoDB.")
        return mmd
    
def get_html (section: int):
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
        mmd_path = doc.mmd_path
        html_path = doc.html_path
        mmd_cmd = ['multimarkdown', '-f', '--nolabels', '-o', html_path, mmd_path]
        log.debug(f"Multimarkdown Command:\n{mmd_cmd}")
        try:
            result = run(mmd_cmd, capture_output=True, text=True)
        except Exception as e:
            log.error("Unable to create html from section {section}'s multimarkdown.\n\n{e}")
            sys.exit(e)
            
        else:
            with open (html_path, 'r') as infile:
                html = infile.read()
            doc.html = html
            doc.save()
            log.debug("Saved Section {section}'s HTML to disk and MongoDB.")
