# > superforge/core/defaultdoc.py

# > Dependancies
import os
from enum import Enum
from json import dump, loads
from platform import platform
from pprint import pprint
from timeit import timeit

from black import err
from dotenv import load_dotenv
from mongoengine import Document, connect, disconnect_all
from mongoengine.fields import IntField, ListField, StringField
from num2words import num2words
from tqdm.auto import tqdm

try:
    # < If run from main()
    import core.book as bk
    import core.chapter as ch
    import core.endofbook as eob
    import core.epubmetadata as epubmd
    import core.metadata as metad
    import core.myaml as myaml
    import core.section as sec
    import core.titlepage as titlepg
    from core.atlas import BASE, sg
    from core.log import errwrap, log
except ImportError:
    # < If run from the core sub-directory
    import book as bk
    import chapter as ch
    import endofbook as eob
    import epubmetadata as epubmd
    import metadata as metad
    import myaml
    import section as sect
    import titlepage as titlepg
    from atlas import BASE, sg
    from log import errwrap, log
    log.debug(f"Imported custom modules.")
load_dotenv(".env")

#.┌─────────────────────────────────────────────────────────────────┐.#
#.│                          Default Doc                            │.#
#.└─────────────────────────────────────────────────────────────────┘.#

class Defaultdoc(Document):
    book = IntField(unique=True, min_value=1, max_value=10)
    book_word = StringField()
    cover = StringField()
    cover_path = StringField()
    default = StringField()
    filename = StringField()
    filepath = StringField()
    input_files = ListField(StringField())
    output = StringField()
    resource_paths = ListField(StringField())
    section1_files = ListField(StringField())
    section2_files = ListField(StringField())
    section_count = IntField(min_value=1, max_value=2)
    sections = ListField(IntField(min_value=1, max_value=17))
    epubmetadata = StringField()
    metadata = StringField()
    default_doc = StringField()
    meta = {"collection": "defaultdoc"}


# > Book Word
@errwrap() #. Verified
def generate_book_word(book: int):
    """
    Generates, retrieves, or updates the word from the given book.

    Args:
        `book` (int):
            The given book.

        `mode` (Optional[str]):
            The mode in which the function is called.

    Returns:
        `book_word` (str):
            The written version of the given book.
    """
    return str(num2words(book)).capitalize()


# > Cover
@errwrap() #. Verified
def generate_cover(book: int):
    """
    Generate the filename of the given book's coverpage.

    Args:
        `book` (int):
            The given book.

    Returns:
        `cover` (str):
            The filename of the given book's coverpage.
    """
    cover = f"cover{book}.png"
    return cover

@errwrap() #. Verified
def get_cover(book: int):
    """
    Retrieve the filename fo the given book's coverpage from MongoDB.

    Args:
        `book` (int):
            The given book.

    Returns:
        `cover` (str):
            The filename fo the given book's coverpage retrieved from MongoDB.
    """
    sg()
    for doc in Defaultdoc.objects(book=book):
        return doc.cover

@errwrap() #. Verified
def save_cover(book: int):
    """
    Generate the filename of the the given book's cover page and update it's value in MongoDB.

    Args:
        `book` (int):
            The given book.

    Returns:
        `cover` (str):
            The filename of the given book's cover page.
    """
    cover = generate_cover(book)
    log.debug(f"Updating Book {book}'s cover: {cover}")

    sg()
    for doc in Defaultdoc.objects(book=book):
        doc.cover = cover
        doc.save()
        log.debug(f"Saved Book {book}'s updated coverpage to MongoDB.")
    return cover


# > Cover Path
@errwrap()  #. Verified
def generate_cover_path(book: int):
    """
    Generate the filepath for the cover page of the given book.

    Args:
        `book` (int):
            The given book.

    Returns:
        `cover_path` (str):
            The filepath of the cover page from the given book.
    """
    cover = generate_cover(book)
    book_zfill = str(book).zfill(2)
    book_dir = f"book{book_zfill}"
    return f"{BASE}/books/{book_dir}/Images/{cover}"


@errwrap() #. Verified
def generate_output(book: int):
    '''
    Generate the filename for the the epub of the given book.

    Args:
        `book` (int):
            The given book.

    Returns:
        `output` (str): 
            The filename for the given book's epub.
    '''
    sg()
    for doc in Defaultdoc.objects(book=book):
        log.debug(f"Accessed Book {book}'s MongoDB Default Document.")
        return doc.output
        

@errwrap()
def generate_section_files(section: int, filepath: bool=False):
    '''
    Generates a list of filenames/filepaths of a given section's Sectino Page followed by it's chapters.
        
    Args:
        `section` (int):
            The given section.
        `filepath` (bool):
            Whether to generate the the full filepath for the files. Defaults to is False.
        
    Returns:
        `section_files` (list[str]):
            The order contend of a the given section.
    
    '''
    sg()
    chapter_count= {}
    
    for doc in sect.Section.objects(section=section):
        # > Section page
        if filepath:
            section_page = doc.html_path
        else:
            section_page = f'{doc.filename}.html'
        section_files = [section_page]
        
        # > Retrieve list of chapter numbers
        section_chapters = doc.chapters # list[int]
        chapter_count[section] = len(section_chapters)
        
        #> Loop through chapters in section chapter
        desc = f"Generating Section {section}'s Chapter List"
        for chapter_number in tqdm(section_chapters, unit='ch', desc=desc):
            chapter_str = str(chapter_number).zfill(4)
            if filepath:
                book = ch.generate_book(chapter_number)
                filepath = f"{BASE}/books/book{book}/html/chapter-{chapter_str}.html"
                section_files.append(filepath)
            else:
                filename = f"chapter-{chapter_str}.html"
                section_files.append(filename)
        
        #> Log Section Files
        result = f"Section {section}'s files:\n"
        for item in section_files:
            result += f"- {item}\n"
        log.info(result)
        
        return section_files
    
    
    
section_files = generate_section_files(10, filepath=True)


