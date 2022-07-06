# > superforge/core/defaultdoc.py

# > Dependancies
import os
from enum import Enum
from platform import platform
from pprint import pprint

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

    log.debug(f"Imported custom modulesfrom core.")
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
    from atlas import BASE
    from log import errwrap, log

    log.debug(f"Imported custom modules.")

load_dotenv("/Users/maxludden/dev/py/superforge/.env")


@errwrap(entry=False, exit=False)
def sg(database: str = "SUPERGENE", test: bool = False):
    disconnect_all()
    URI = os.environ.get(database)
    if test:
        log.info(f"URI: {URI}")
    try:
        connect("SUPERGENE", host=URI)
        log.debug(f"URI: {URI}\n\nConnected to MongoDB.")
    except ConnectionError:
        raise ConnectionError


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
@errwrap()
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
@errwrap()
def generate_cover(book: int, save: bool = True):
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


@errwrap()
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


@errwrap()
def patch_cover(book: int):
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

    sg(test=True)
    for doc in Defaultdoc.objects(book=book):
        doc.cover = cover
        doc.save()
        log.debug(f"Saved Book {book}'s updated coverpage to MongoDB.")
    return cover


# > Cover Path
@errwrap()
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


sg(test=True)
count = Defaultdoc.objects.count()
log.warning(f"Number of Default Documents: {count}")
for doc in Defaultdoc.objects():
    book_word = generate_book_word(doc.book)
    doc.book_word = book_word
    doc.save()
    log.info(f"Book: {doc.book} | Book Word: {book_word}")


# sg()
# for doc in Defaultdoc.objects():
#     pprint(doc)
