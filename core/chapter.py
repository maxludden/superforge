# core/chapter.py

import os
import re
import sys
from subprocess import run

from dotenv import load_dotenv
from mongoengine import Document
from mongoengine.fields import EnumField, IntField, StringField
from tqdm.auto import tqdm

from core.log import log, errwrap
from core.atlas import sg, max_title

load_dotenv()
base = '/Users/maxludden/dev/py/superforge/books'

#.
#.           888                        d8                  
#.   e88'888 888 ee   ,"Y88b 888 88e   d88    ,e e,  888,8, 
#.  d888  '8 888 88b "8" 888 888 888b d88888 d88 88b 888 "  
#.  Y888   , 888 888 ,ee 888 888 888P  888   888   , 888    
#.   "88,e8' 888 888 "88 888 888 88"   888    "YeeP" 888    
#.                           888                            
#.                           888                            

class Chapter(Document):
    chapter = IntField(Required=True, unique=True)
    section = IntField()
    book = IntField()
    title = StringField(max_length=500, Required=True)
    text = StringField(Required=True)
    filename = StringField()
    mmd_path = StringField()
    html_path = StringField()
    mmd = StringField()
    html = StringField()
    
    def get_values(self):
        """This function returns a given chapter's metadata."""
        values = {
            "chapter": self.chapter,
            "section": self.section,
            "book": self.book,
            "title": self.title,
            "filename": self.filename,
            "mmd_path": self.mmd_path,
            "html_path": self.html_path
        }
        return values

@errwrap()
def make_section(chapter):
    """Determines the given chapter's section."""

    if chapter <= 424:
        return 1
    elif chapter <= 882:
        return 2
    elif chapter <= 1338:
        return 3
    elif chapter <= 1679:
        return 4
    elif chapter <= 1711:
        return 5
    elif chapter <= 1821:
        return 6
    elif chapter <= 1960:
        return 7
    elif chapter <= 2165:
        return 8
    elif chapter <= 2204:
        return 9
    elif chapter <= 2299:
        return 10
    elif chapter <= 2443:
        return 11
    elif chapter <= 2639:
        return 12
    elif chapter <= 2765:
        return 13
    elif chapter <= 2891:
        return 14
    elif chapter <= 3033:
        return 15
    elif chapter <= 3303:
        return 16
    elif chapter <= 3462:
        return 17
    else:
        log.error(
            f"\tInvalid chapter number",
            args={"chapter": chapter, "function": "chapter_get_section"},
        )
        sys.exit(
            {
                "-2": {
                    "error": "Invalid Input Error",
                    "function": "Chapter.get_section",
                    "chapter": chapter
                }
            }
        )

@errwrap()
def get_book(chapter: int):
    """Determine the book of a given chapter."""

    section = make_section(chapter)
    log.debug(f"Section: {section}")
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
        log.error(
            "\tInvalid Chapter Number",
            args={"chapter": chapter, "function": "chapter,get_book"},
        )
        sys.exit(
            {
                "-3": {
                    "error": "Invalid Input Error",
                    "function": "chapter.get_book",
                    "chapter": chapter,
                }
            }
        )

@errwrap()
def make_filename(chapter: int):
    """Generate the filename for the given chapter."""
    chapter_zfill = str(chapter).zfill(4)
    return f"chapter-{chapter_zfill}"

@errwrap()
def make_mmd_path(book: int, filename: str):
    """Generates the path to where the give chapter's multimarkdown will be stored."""
    book_dir = str(book).zfill(2)
    mmd_path = f"{base}book{book_dir}/mmd/{filename}.md"
    return mmd_path

@errwrap()
def make_html_path(book: int, filename: str):
    """Generates the path to where the given chapter's html will be stored."""
    book_dir = str(book).zfill(2)
    html_path = f"{base}book{book_dir}/html/{filename}.html"
    return html_path

@errwrap()
def make_mmd(doc: Chapter):
    """Generates the multimarkdown string for the given chapter."""

    # Multimarkdown Metadata
    meta = f"Title:{doc.title} \nChapter:{doc.chapter} \nSection:{doc.section} \nBook:{doc.book} \nCSS:../Styles/style.css \nviewport: width=device-width\n\n"
    
    # ATX Headers
    img = """<figure>\n\n<img src="../Images/gem.gif" alt="gem" id="gem" width="120" height="60" />\n\n</figure>\n\n"""
    
    atx = f"## {doc.title}\n### Chapter {doc.chapter} \n{img}\n\n"
    
    # Chapter Text
    text = f"{doc.text}\n"
    
    # Concatenate Multimarkdown
    mmd = f"{meta}{atx}{text}"
    
    with open (doc.mmd_path, 'w') as outfile:
        outfile.write (doc.mmd)
    log.debug("Wrote Chapter {doc.chapter}'s multimarkdown to disk.")
    return mmd

@errwrap() 
def make_html(doc):
    """Generate the HTML for a given chapter."""
    log.debug(doc.get_values())
    mmd_cmd = [
        "multimarkdown", "-f", "--nolabels", "-o", f"{doc.html_path}", f"{doc.mmd_path}"
    ]
    log.debug(f"MMD: {doc.mmd_path}")
    log.debug(f"HTML: {doc.html_path}")
    log.debug(f"Multitmarkdown Command: {mmd_cmd}")
    try:
        result = run(mmd_cmd)
    except OSError as ose:
        log.error(ose, traceback=True)
        sys.exit("OS Error occured in the proccess of creating HTML for Chapter {doc.chapter}.")
    except Exception as e:
        log.error(e)
        sys.exit("Error occured in the proccess of creating HTML for Chapter {doc.chapter}")
    
    else:
        with open (doc.html_path, 'r') as chapter:
            html = chapter.read()
        return html


@errwrap()
def write_md(doc: Chapter):
    """Writes Chapter's multimarkdown to disk."""
    
    log.debug(doc.get_values())
    
    chapter = str(doc.chapter)
    filepath = doc.mmd_path
    log.debug(f'"Multimarkdown Filepath": "{filepath}"')
    try:
        with open (filepath, 'w') as outfile:
            outfile.write(doc.mmd)
    except OSError as e: 
        log.error("Error writing Chapter {chapter}'s multimarkdown to disk.")
        sys.exit("Unable to write Chapter {chapter}'s multimarkdown to disk.")
    else:
        log.debug("Successfully wrote Chapter {chapter}'s multimarkdown to disk.")
        return doc.mmd_path
