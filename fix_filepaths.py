# utilities/fix_filepaths.py
from pprint import pprint

from dotenv import load_dotenv
from tqdm.auto import tqdm

import core.book as bk
import core.chapter as ch
import core.endofbook as eob
import core.epubmetadata as epubmd
import core.metadata as metad
import core.myaml as myaml
import core.section as sec
import core.titlepage as titlepage
from core.atlas import BASE, sg
from core.chapter import Chapter
from core.cover import Coverpage
from core.log import errwrap, log
from core.titlepage import Titlepage
from utilities.yay import superyay, yay

load_dotenv(".env")

# .┌─────────────────────────────────────────────────────────────────┐. #
# .│                        Fix Filepaths                            │. #
# .└─────────────────────────────────────────────────────────────────┘. #
def dp(msg: str):
    pprint(msg, indent=4)

@errwrap()
def generate_section(chapter: int):
    '''
    Determines the given chapter's section.

    Args:
        `chapter` (int):
            The given chapter.
            
    Raises:
        `ValueError`: Invalid Chapter Number

    Returns:
        `section` (int): 
            The section that the given chapter belongs to.
    '''
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
        raise ValueError("Invalid Chapter", f"\nChapter: {chapter}")

@errwrap()
def generate_book(chapter: int):
    '''
    Generate the book for a given chapter.

    Args:
        `chapter` (int):
            The given chapter.

    Raises:
        `ValueError`: Invalid Section Number

    Returns:
        `book` (int): 
            The book of the given chapter
    '''

    section = generate_section(chapter)
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
        raise ValueError("Invalid Section Input.", f'Section: {section}')


@errwrap()
def chapter_generate_html_path(chapter: int, book: int):
    book_str = str(book).zfill(2)
    book_dir = f"book{book_str}"
    chapter_str = str(chapter).zfill(4)
    filename = f"chapter-{chapter_str}.html"
    log.debug(f"Chapter {chapter}'s Filename: {filename}")
    html_path = f"{BASE}/books/{book_dir}/html/{filename}"
    log.debug(f"Chapter {chapter}: {html_path}")
    return html_path


@errwrap()
def fix_chapter_html_paths():
    sg()
    chapter_position = 0
    for doc in tqdm(Chapter.objects(), unit='ch', desc="Fixing Chapter Filepaths"):
        chapter_position += 1
        chapter = doc.chapter
        book = doc.book
        doc.html_path = chapter_generate_html_path(chapter, book)
        doc.save()
        
        msg = f"Updated Chapter {chapter}'s Filepath in MongoDB."
        if chapter_position % 50 == 0:
            log.info (msg)
        else:
            log.debug(msg)

@errwrap()
def chapter_generate_md_path(chapter: int, book: int):
    book_str = str(book).zfill(2)
    book_dir = f"book{book_str}"
    chapter_str = str(chapter).zfill(4)
    filename = f"chapter-{chapter_str}.md"
    log.debug(f"Chapter {chapter}'s Filename: {filename}")
    html_path = f"{BASE}/books/{book_dir}/md/{filename}"
    log.debug(f"Chapter {chapter}'s md_path: {html_path}")
    return html_path

@errwrap()
def fix_chapter_md_paths():
    sg()
    chapter_position = 0
    for doc in tqdm(Chapter.objects(), unit='ch', desc="Fixing Chapter Filepaths"):
        chapter_position += 1
        chapter = doc.chapter
        book = doc.book
        doc.html_path = chapter_generate_md_path(chapter, book)
        doc.save()
        
        msg = f"Updated Chapter {chapter}'s Filepath in MongoDB."
        log.debug(msg)

#> Titlepage
@errwrap()
def fix_titlepage_paths(book: int):
    '''
    Generate the correct filepaths for the md and html of the given book's titlepage.

    Args:
        `book` (int):
            The give book.
    '''
    book_str = str(book).zfill(2)
    book_dir = f"book{book_str}"
    titlepage_filename = f"titlepage-{book_str}"
    md_path = f"{BASE}/books/{book_dir}/md/{titlepage_filename}.md"
    html_path = f"{BASE}/books/{book_dir}/html/{titlepage_filename}.html"
    paths = {
        book: {
            "md": md_path,
            "html": html_path
        }
    }
    dp(paths)
    
#> Coverpage
@errwrap()
def fix_coverpage_html_path(book: int):
    '''
    Generate the correct filepaths for the md and html of the given book's coverpage.

    Args:
        `book` (int):
            The give book.
    '''
    book_str = str(book).zfill(2)
    book_dir = f"book{book_str}"
    cover_filename = f"cover{book}"
    html_path = f"{BASE}/books/{book_dir}/html/{cover_filename}.html"
    return html_path
    
def fix_covers():
    sg()
    for doc in Coverpage.objects():
        book = doc.book
        log.debug(f"Updating Book {book}'s html_path.")
        html_path = fix_coverpage_html_path(book)
        log.debug(f"Generated HTML_PATH: {html_path}")
        doc.html_path = html_path
        doc.save()
        log.info(f"Book {book} complete")
    
#> Epub Metadata
@errwrap()
def fix_epubmeta_paths():
    sg()
    for doc in epubmd.Epubmeta.objects():
        doc.html_path = f"{BASE}/{doc.filepath}"
        doc.filepath = doc.html_path
        doc.save()
        log.debug(f"Added html_path to Book {doc.book}'s Epub Metadata: {doc.html_path}")
        
    yay()

    
#> Epub Metadata
@errwrap()
def fix_metadata_paths():
    sg()
    for doc in metad.Meta.objects():
        doc.html_path = f"{BASE}/{doc.filepath}"
        doc.filepath = doc.html_path
        doc.save()
        log.debug(f"Added html_path to Book {doc.book}'s Epub Metadata: {doc.html_path}")
        
    yay()
