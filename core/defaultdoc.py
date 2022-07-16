# > superforge/core/defaultdoc.py

# > Dependancies
import os
from enum import Enum
from json import dump, loads
from platform import platform
from pprint import pprint
from timeit import timeit

from dotenv import load_dotenv
from mongoengine import Document, connect, disconnect_all
from mongoengine.fields import IntField, ListField, StringField
from num2words import num2words
from tqdm.auto import tqdm, trange

try:
    # < If run from main()
    import core.book as bk
    import core.chapter as ch
    import core.endofbook as eob
    import core.epubmetadata as epubmeta
    import core.metadata as meta
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
    import epubmetadata as epubmeta
    import metadata as meta
    import myaml
    import section as sect
    import titlepage as titlepg
    from atlas import BASE, sg
    from log import errwrap, log

    log.debug(f"Imported custom modules.")
load_dotenv(".env")

# .┌─────────────────────────────────────────────────────────────────┐.#
# .│                          Default Doc                            │.#
# .└─────────────────────────────────────────────────────────────────┘.#
class InvalidBookError(Exception):
    pass

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


@errwrap()
def generate_filename(book: int):
    """
    Generates the filename of the given book's default file.

    Args:
        `book` (int):
            The given book.

    Returns:
        `filename` (str):
            The filename of the given book's default file.
    """
    return f"sg{book}.yaml"


@errwrap()
def generate_filepath(book: int, save: bool = False):
    """
    Generates the filepath of the given book's default file.

    Args:
        `book` (int):
            The given book.
        `save` (bool, optional):
            Whether to save the filepath to MongoDB. Defaults to False.

    Returns:<
        `filepath` (str):
            The filepath of the given book's default file.
    """
    book_str = str(book).zfill(2)
    book_dir = f"{BASE}/books/book{book_str}"
    filepath = f"{book_dir}/sg{book}.yaml"
    log.debug(f"Generated filepath:\n<code>{filepath}</code>")
    if save:
        sg()
        for doc in Defaultdoc.objects(book=book):
            doc.filepath = filepath
            doc.save()
            log.debug(f"Saved Book {book}'s Default File's Filepath.")
    return filepath


@errwrap()
def generate_book(section: int):
    match int(section):
        case 1:
            return 1
        case 2:
            return 2
        case 3:
            return 3
        case 4 | 5:
            return 4
        case 6 | 7:
            return 5
        case 8 | 9:
            return 6
        case 10 | 11:
            return 7
        case 12 | 13:
            return 8
        case 14 | 15:
            return 9
        case 16 | 17:
            return 10
        case _:
            raise ValueError("Invalid Section Input.", f"Section: {section}")


@errwrap()
def generate_sections(book: int):
    """
    Generates a list of sections of a given book.

    Args:
        `book` (int):
            The given book.

    Raises:
        `ValueError`:
            Invalid Book Input. Valid books are 1-10.

    Returns:
        `sections` (list[int]):
            The sections of a given book.
    """
    valid_books = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    if book not in valid_books:
        raise ValueError(f"Invalid book: {book}\n\nValid books are 1-10.")
    sections = []
    match book:
        case 1:
            return [1]
        case 2:
            return [2]
        case 3:
            return [3]
        case 4:
            return [4, 5]
        case 5:
            return [6, 7]
        case 6:
            return [8, 9]
        case 7:
            return [10, 11]
        case 8:
            return [12, 13]
        case 9:
            return [14, 15]
        case 10:
            return [16, 17]


@errwrap()
def get_sections(book: int):
    sg()
    doc = Defaultdoc.objects(book=book).first()
    return doc.sections


# > Book Word
@errwrap()  # . Verified
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
@errwrap()  # . Verified
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


@errwrap()  # . Verified
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


@errwrap()  # . Verified
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
@errwrap()  # . Verified
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
    return f"${{.}}/books/{book_dir}/Images/{cover}"


@errwrap()  # . Verified
def generate_output(book: int):
    """
    Generate the filename for the the epub of the given book.

    Args:
        `book` (int):
            The given book.

    Returns:
        `output` (str):
            The filename for the given book's epub.
    """
    sg()
    for doc in Defaultdoc.objects(book=book):
        log.debug(f"Accessed Book {book}'s MongoDB Default Document.")
        return doc.output


@errwrap()  # . Verified
def generate_section_files(section_to_get: int, filepath: bool = False):
    """
    Generates a list of filenames/filepaths of a given section's Sectino Page followed by it's chapters.

    Args:
        `section` (int):
            The given section.
        `filepath` (bool):
            Whether to generate the the full filepath for the files. Defaults to is False.

    Returns:
        `section_files` (list[str]):
            The order contend of a the given section.

    """
    sg()
    chapter_count = {}

    for doc in sect.Section.objects(section=section_to_get):
        # > Section page
        if filepath:
            section_page = doc.html_path
            log.debug(f"Adding section filepath to input_files: {section_page}")
        else:
            section_page = f"{doc.filename}.html"
            log.debug(f"Adding section filename to input_files: {section_page}")
        section_files = [
            section_page
        ]  # Declare section_files and initiates with section page.

        # > Retrieve list of chapter numbers
        section_chapters = doc.chapters  # list[int]
        sc_result = f"Section {section_to_get}'s Chapter List:\n"
        for section_chapter in section_chapters:
            sc_result += f"- {section_chapter}\n"
        log.debug(sc_result)
        chapter_count[section_to_get] = len(section_chapters)

        # > Loop through chapters in section chapter
        desc = f"Generating Section {section_to_get}'s Chapter List"
        for chapter_number in tqdm(section_chapters, unit="ch", desc=desc):
            chapter_str = str(chapter_number).zfill(4)
            if filepath:
                book = generate_book(section_to_get)
                filepath = f"${{.}}/books/book{book}/html/chapter-{chapter_str}.html"
                section_files.append(filepath)
            else:
                filename = f"chapter-{chapter_str}.html"
                section_files.append(filename)

        # > Log Section Files
        result = f"Section {section_to_get}'s files:\n"
        for item in section_files:
            result += f"- {item}\n"
        log.debug(result)

        return section_files


@errwrap()
def get_section_files(section: int):
    sg()
    for doc in sect.Section.objects(section=section):
        return doc.section_files


@errwrap()  # . Verified
def generate_input_files_single(book: int, save: bool = False):
    """
    Generates a list of input files of a given book.

    Args:
        `book` (int):
            The given book.

    Raises:
        `ValueError`:
            Invalid Book Input. Valid books are 1, 2, and 3.

    Returns:
        `input_files` (list[str]):
            The input files of a given book.
    """
    valid_books = [1, 2, 3]
    if book in valid_books:
        book_str = str(book).zfill(2)
        input_files = [f"cover{book}.html", f"titlepage-{book_str}.html"]
        section_files = generate_section_files(book)
        input_files.extend(section_files)
        input_files.append(f"endofbook-{book_str}.html")
        if save:
            sg()
            for doc in Defaultdoc.objects(book=book):
                doc.input_files = input_files
                doc.save()
        return input_files
    else:
        raise ValueError(f"Invalid book: {book}\n\nValid books are 1, 2, and 3.")


@errwrap()  # . Verified
def generate_input_files_multiple(book: int, save: bool = False):
    """
    Generates a list of input files of a given book.

    Args:
        `book` (int):
            The given book.

    Raises:
        `ValueError`:
            Invalid Book Input. Valid books are 4-10.

    Returns:
        `input_files` (list[str]):
            The input files of a given book.
    """
    valid_books = [4, 5, 6, 7, 8, 9, 10]
    if book not in valid_books:
        raise ValueError(f"Invalid book: {book}\n\nValid books are 4-10.")
    input_files = []
    for doc in Defaultdoc.objects(book=book):
        book_str = str(book).zfill(2)
        input_files.append(f"cover{book}.html")
        input_files.append(f"titlepage-{book_str}.html")
        sections = doc.sections
        log.debug(f"Book {book}'s sections: {sections}")
        for section in sections:
            section_files = generate_section_files(section)
            input_files.extend(section_files)
        input_files.append(f"endofbook-{book_str}.html")

        result = f"Book {book}'s files:\n"
        for item in input_files:
            result += f"- {item}\n"

        log.debug(result)

    if save:
        sg()
        for doc in Defaultdoc.objects(book=book):
            doc.input_files = input_files
            doc.save()
    return input_files


@errwrap()
def get_input_files(book: int):
    """
    Retrieve a given book's input files from MongoDB.

    Args:
        `book` (int)
            The given book

    Returns:
        `input_files` (list[str]):
            The given book's input files.
    """
    sg()
    for doc in Defaultdoc.objects(book=book):
        return doc.input_files


def generate_resource_paths(book: int, save: bool = False):
    book_str = str(book).zfill(2)
    book_dir = f"${{.}}/books/book{book_str}"
    resource_files = ["."]

    # > Non-content files
    # Images
    resource_files.append(f"{book_dir}/Images/cover{book}.png")
    resource_files.append(f"{book_dir}/Images/title.png")
    resource_files.append(f"{book_dir}/Images/gem.gif")

    # Fonts
    resource_files.append(f"{book_dir}/Styles/Century Gothic.ttf")
    resource_files.append(f"{book_dir}/Styles/Photograph Signature.ttf")

    # CSS
    resource_files.append(f"{book_dir}/Styles/style.css")

    # Metadata
    resource_files.append(f"{book_dir}/html/meta{book}.yaml")
    resource_files.append(f"{book_dir}/html/epub-meta{book}.yml")

    # > Content files
    sg()
    for doc in Defaultdoc.objects(book=book):
        input_files = doc.input_files
        for input_file in input_files:
            resource_files.append(f"{book_dir}/html/{input_file}")

    result = f"Book {book}'s resource files:\n"
    for resource in resource_files:
        result += f"- {resource}\n"

    log.debug(result)

    if save:
        sg()
        for doc in Defaultdoc.objects(book=book):
            doc.resource_paths = resource_files
            doc.save()

    log.info(f"Finished generating resource files for book {book}.")

    return resource_files


@errwrap()
def get_resource_paths(book: int):
    """
    Retrieve a given book's resource files from MongoDB.

    Args:
        `book` (int)
            The given book):

    Returns:
        `resource_paths` (list[str]):
            The given book's resource files.
    """
    sg()
    for doc in Defaultdoc.objects(book=book):
        return doc.resource_paths


@errwrap()
def load_meta(book: int):
    """
    Loads the metadata of a given book from MongoDB.

    Args:
        `book` (int)
            The given book):

    Returns:
        `meta` (dict):
            The given book's metadata.
    """
    sg()
    for doc in meta.Metadata.objects(book=book):
        metadata = doc.text
        log.debug(f"Retrieved Metadata for Book {book}:\n\n {metadata}")
    sg()
    for doc in epubmeta.Epubmeta.objects(book=book):
        epub_metadata = doc.text
        log.debug(f"Retrieved ePub Metadata for Book {book}:\n\n {epub_metadata}")
    sg()
    for doc in Defaultdoc.objects(book=book):
        doc.metadata = metadata
        doc.epubmetadata = epub_metadata
        doc.save()
        log.info(f"Updated Book {book}'s defualtdoc with Metadata and ePub Metadata.")


@errwrap()
def generate_default_doc(book: int, save: bool = False):
    """
    Generates the default doc for a given book.

    Args:
        `book` (int):
            The given book.

    Raises:
        `ValueError`:
            Invalid Book Input. Valid books are 1-10.

    Returns:
        `default_doc` (dict):
            The default doc for a given book.
    """
    # > Validate book
    valid_books = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    if book not in valid_books:
        raise InvalidBookError(f"Invalid book: {book}\nValid books are 1-10.")
    
    sg()
    mongodefault = Defaultdoc.objects(book=book).first()
    
    default_doc = {
        "from": "html",
        "to:": "epub",
        "output-file": mongodefault.output,
        "input-files": mongodefault.input_files,
        "standalone": True,
        "self-contained": True,
        "resource-files": mongodefault.resource_paths,
        "toc": True,
        "toc-depth": 2,
        "epub-chapter-level":2,
        "epub-cover-image": mongodefault.cover,
        "epub-fonts": [
            "Urbanist-Italic.ttf",
            "Urbanist-Regular.ttf",
            "Urbanist-thin.ttf",
            "Urbanist-ThinItalic.ttf",
            "White Modesty.ttf"
        ],
        "epub-metadata": mongodefault.epubmetadata,
        "metadata-file": [f"epub-meta{book}.yaml",f"meta{book}.yaml"],
        "css": [
            "style.css"
        ]
    }
    filepath = mongodefault.html_path
    with open (filepath, "w") as outfile:
        myaml.dumps(default_doc, outfile)
        
generate_default_doc(1, True)