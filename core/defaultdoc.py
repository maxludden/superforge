# > superforge/core/defaultdoc.py

# > Dependancies
import os
from enum import Enum
from json import dump, loads
from platform import platform
from pprint import pprint
from timeit import timeit
from turtle import title

from dotenv import load_dotenv
from mongoengine import Document, connect, disconnect_all
from mongoengine.fields import IntField, ListField, StringField
from num2words import num2words
from tqdm.auto import tqdm, trange
from alive_progress import alive_bar

import core.book as book_
import core.chapter as ch
import core.endofbook as eob
import core.epubmetadata as epubmeta
import core.metadata as meta
import core.myaml as myaml
import core.section as sec
import core.titlepage as titlepg
from core.base import BASE
from core.atlas import max_title, sg
from core.log import errwrap, log


load_dotenv()

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
    title = StringField()
    meta = {"collection": "defaultdoc"}


@errwrap()
def generate_filename(book: int, save: bool = False):
    """
    Generates the filename of the given book's default file.

    Args:
        `book` (int):
            The given book.

    Returns:
        `filename` (str):
            The filename of the given book's default file.
    """
    filename = f"sg{book}.yml"
    if save:
        sg()
        doc = Defaultdoc.objects(book=book).first()
        doc.filename = filename
        doc.save()
    log.debug(f"Generated Book {book}filename for book {book}: {filename}")
    return filename


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
    filepath = f"{book_dir}/sg{book}.yml"
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
def generate_output(book: int, save: bool = False):
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
    book_doc = book_.Book.objects(book=book).first()
    output = f"{book_doc.title}.epub"
    log.debug(f"Generated output filename:\n<code>{output}</code>")

    if save:
        sg()
        doc = Defaultdoc.objects(book=book).first()
        doc.output = output
        doc.save()
        log.debug(f"Saved Book {book}'s output file's filename to MongoDB.")

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
    book_dir = f"${{.}}"
    resource_files = ["."]

    # > Non-content files
    # Images
    resource_files.append(f"{book_dir}/Images/cover{book}.png")
    resource_files.append(f"{book_dir}/Images/title.png")
    resource_files.append(f"{book_dir}/Images/gem.gif")

    # Fonts
    resource_files.append(f"{book_dir}/Styles/Urbanist-Regular.ttf")
    resource_files.append(f"{book_dir}/Styles/Urbanist-Thin.ttf")
    resource_files.append(f"{book_dir}/Styles/Urbanist-Italit.ttf")
    resource_files.append(f"{book_dir}/Styles/Urbanist-ThinItalic.ttf")
    resource_files.append(f"{book_dir}/Styles/White Modestry.ttf")
    
    # CSS
    resource_files.append(f"{book_dir}/Styles/style.css")

    # Metadata
    resource_files.append(f"{book_dir}/yaml/meta{book}.yml")
    resource_files.append(f"{book_dir}/yaml/epub-meta{book}.yml")

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

    log.debug(f"Finished generating resource files for book {book}.")

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
        log.debug(f"Updated Book {book}'s defualtdoc with Metadata and ePub Metadata.")


@errwrap()
def generate_default_doc_f(book: int, save: bool = False):
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
    output = mongodefault.output
    

    default_1= f"from: html\nto: epub\n  \noutput-file: {output}"

    input_file_list = mongodefault.input_files
    input_files = f"\n  \ninput-files:\n"
    for file in input_file_list:
        input_files = f"{input_files}\n- {file}"

    default3 = f"\n\nstandalone: true\nself-contained: true\n"

    resource_files = "resource-files:\n- ."
    resource_file_list = mongodefault.resource_paths
    for file in resource_file_list:
        resource_files = f"{resource_files}\n- {file}"

    epub = f"toc: true\ntoc-depth: 2\nepub-chapter-level: 2\nepub-cover-image: cover{book}.png\n  "

    fonts = f"\nepub-fonts:\n- Urbanist-Italic.ttf\n- Urbanist-Regular.ttf\n- Urbanist-Thin.ttf\n- Urbanist-ThinItalic.ttf\n- White Modesty.ttf\n"

    meta = f"epub-metadata: {mongodefault.epubmetadata}\nmetadata-files:\n- meta{book}.yml\n- epub-meta{book}.yml\n"

    css = "css-files:\n- style.css\n"

    default_doc = f"{default_1}\n{input_files}\n{default3}\n{resource_files}\n{epub}\n{fonts}\n{meta}\n{css}"

    filepath = mongodefault.filepath
    yaml_str = myaml.dump(default_doc)
    with open(filepath, "w") as outfile:
        outfile.write(yaml_str)

    if save:
        sg()
        default_mongo_doc = Defaultdoc.objects(book=book).first()
        default_mongo_doc.default_doc = default_doc
        default_mongo_doc.save()
        log.debug(f"Updated Book {book}'s defualtdoc with default doc.")
    return default_doc


@errwrap()
def generate_cover(book: int, save: bool = False):
    cover = f"cover{book}.png"
    if save:
        sg()
        doc = Defaultdoc.objects(book=book).first()
        doc.cover = cover
        doc.save()
    return cover


@errwrap()
def generate_cover_path(book: int, save: bool = False):
    sg()
    for doc in Defaultdoc.objects(book=book):
        book = doc.book
        book_str = str(book).zfill(2)
        book_dir = f"book{book_str}"
        cover_path = f"{BASE}/books/{book_dir}/Images/cover{book}.png"

        if save:
            doc.cover_path = cover_path
            doc.save()

        return cover_path
        
         
@errwrap()
def generate_title(book: int, save: bool = False):
    """
    Generates the default doc for a given book.

    Args:
        `book` (int):
            The given book.
        `save` (bool):
            Whether or not to save the default doc to MongoDB.
        `write` (bool):
            Whether or not to write the default doc to a file.

    Raises:
        `ValueError`:
            Invalid Book Input. Valid books are 1-10.

    Returns:
        `default_doc` (dict):
            The default doc for a given book.
    """
    bar_title = f"Generating title for Book {book}"
    bar_title_length = len(bar_title)
    title_length = bar_title_length + 1
    sg()
    doc = book_.Book.objects(book=book).first()
    if doc is None:
        raise InvalidBookError(f"Invalid book: {book}\nValid books are 1-10.")

    title = doc.title
    log.debug(f"Retrieved title for Book {book}")

    if save:
        sg()
        default_ = Defaultdoc.objects(book=book).first()
        default_.title = title
        default_.save()
        log.debug(f"Updated Book {book}'s defualtdoc with title.")

    return title


def get_input_files(book: int) -> str:
    sg()
    doc = Defaultdoc.objects(book=book).first()
    inputf = "input-files:"
    for file in doc.input_files:
        inputf = f"{inputf}\n- {file}"
    log.debug(f"Retrieved input files for Book {book}:</code>\n{inputf}</code>")
    return inputf

def get_resource_path(book: int) -> str:
    sg()
    doc = Defaultdoc.objects(book=1).first()
    resourcef = "resource-files:"
    for file in doc.resource_paths:
        resourcef = f"{resourcef}\n- {file}"
    log.debug(f"Retrieved resource path for Book {book}:</code>\n{resourcef}</code>")
    return resourcef
    
def generate_default_doc(book: int, save: bool = True, write: bool = True):
    sg()
    doc = Defaultdoc.objects(book=book).first()
    
    #. Read default variable from MongoDB
    #> Book
    book = doc.book
    book_str = str(book).zfill(2)
    book_dir = f"book{book_str}"
    
    #> Output
    output = doc.output
    title = doc.title
    
    #> Book Word
    book_word = doc.book_word
    
    #> Cover
    cover = doc.cover
    cover_path = doc.cover_path
    
    #> Filename and Path
    filepath = doc .filepath
    
    #> Input FIles
    input_files = get_input_files(book)
    
    #> Resource_Files
    resource_path = get_resource_path(book)

    #> Epub
    epubmetadata = doc.epubmetadata 
    #> Metadata
    metadata = doc.metadata
    
    #> CSS
    css = "css:\n- style.css\n..."
    
    #> Default Doc
    default = f"---\nfrom: html\nto: epub\n\n"
    default = f"{default}\output-file: {book} - {title}.epub\n"
    
    #> Input Files
    default = f"{default}\n{input_files}\n"
    
    #> Mid
    default = f"{default}\nstandalone: true\nself-contained: true\n"
    
    #> Resource Path
    default = f"{default}\n{resource_path}"
    
    #> toc 
    default = f"{default}\n\ntoc: true\ntoc-depth: 2\n\nepub-chapter-level: 2\nepub-cover-image: {cover}\n"
    
    #> epubfonts
    default = f"{default}\nepub-fonts:\n- Urbanist-Italic.ttf\n- Urbanist-Regular.ttf\n- Urbanist-Thin.ttf\n- Urbanist-ThinItalic.ttf\n- White Modesty.ttf\n"
    
    #>Meta
    default = f"{default}\nepub-metadata: epub-meta{book}.yml\n\nmetadata-files:\n- meta{book}.yml\n- epub-meta{book}.yml\n"
    
    #> CSS
    default = f"{default}\ncss-files:\n- style.css\n..."
    
    #> Default Doc
    log.debug(default)
    
    #> Filepath
    if write:

        filepath = doc.filepath
        with open (filepath, "w") as outfile:
            outfile. write(default)
        log.debug(f"Saved Book {book}'s defualtdoc to disk.")
    
    #> Save
    if save:
        sg()
        default_mongo_doc = Defaultdoc.objects(book=book).first()
        default_mongo_doc.default_doc = default
        default_mongo_doc.save()
        log.debug(f"Updated MongoDB with Book {book}'s defualt file.")
    return default
    
# for i in trange(1,11):
#     generate_default_doc(i, save=True, write=True)