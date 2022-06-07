# core/section.py

import sys
from cgitb import html
from enum import unique
from mailbox import MMDF
from subprocess import run

from mongoengine import Document, disconnect_all
from mongoengine.fields import IntField, ListField, StringField
from num2words import num2words

from core.atlas import max_title, sg
from core.log import errwrap, log
from tqdm.auto import tqdm
from markdown2 import markdown as md
from typing import Optional

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
    book = IntField()
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
    book_sections = {
        1:1,
        2:2,
        3:3,
        4:4,
        5:4,
        6:5,
        7:5,
        8:6,
        9:6,
        10:7,
        11:7,
        12:8,
        13:8,
        14:9,
        15:9,
        16:10,
        17:10
    }
    book = book_sections[section]
    return book



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
    if section <= 3:
        return 0
    elif section % 2 == 0:
        return 1
    else:
        return 2
    
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
        meta = f'{meta}\nCSS:../Styles/style.css'
        meta = f'{meta}\nviewport: width=device-width\n\n'
        
        img = '\n\n<figure>\n<img src="../Images/gem.gif" alt="gem" id="gem" width="120" height="60" />\n\n</figure>'
        if part == 0:
            book_word = str(num2words(doc.book)).title()
            atx = f'## Book {book_word} of Super Gene'
            atx = f'{atx}{img}\n\n### Chapter {doc.start} - Chapter {doc.end}\n'
        elif part == 1:
            atx = f'## Part One{img}\n\n### Chapter {doc.start} - Chapter {doc.end}\n\n<br><br><br><br>'
        else:
            atx = f'## Part Two{img}\n\n### Chapter {doc.start} - Chapter {doc.end}\n\n<br><br><br><br>'
            
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
        mmd_path = get_mmd_path(doc.section)
        html_path = get_html_path(doc.section)
        mmd_cmd = ['multimarkdown', '-f', '--nolabels', '-o', html_path, mmd_path]
        log.debug(f"Multimarkdown Command:\n{mmd_cmd}")
        try:
            result = run(mmd_cmd, capture_output=True, text=True)
        except:
            write_html(section)
        else:
            book = str(get_book(doc.section)).zfill(2)
            zsection = str(doc.section).zfill(2)
            html_path = f"/Users/maxludden/dev/py/superforge/books/book{book}/html/section-{zsection}.html"
            with open (html_path, 'r') as infile:
                html = infile.read()
            doc.html = html
            doc.save()
            log.debug("Saved Section {section}'s HTML to disk and MongoDB.")
            
def write_html(section: int, mmd: Optional[str]):
    if not mmd:
        connected = True
        sg()
        for doc in Section.objects(section=section):
            if doc.mmd == "":
                mmd = get_mmd(section)
    html = md(mmd, extras=['metadata'])
    with open (doc.html_path, 'w') as outfile:
        outfile.write(html)
    
    if connected == True:
        disconnect_all()
        
    sg()
    for doc in Section.objects(section=section):
        doc.html = html
        doc.save()
        

@errwrap()
def make_sections():
    """A script to automate the generation of each section page's multimarkdown and convert it into X/HTML.
    """
    sg()
    sections = range(1,18)
    for section in tqdm(sections, unit="section", desc="Writing section pages"):
        for doc in Section.objects(section=section): 
            mmd = get_mmd(section)
            html = get_html(section)
