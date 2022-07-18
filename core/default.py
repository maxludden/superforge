# superforge/core/default.py
#> Imports
import os
import sys
from platform import platform
from pprint import pprint
from tokenize import String
from typing import List

from dotenv import load_dotenv
from icecream import ic
from mongoengine import Document, connect, disconnect_all
from mongoengine.fields import IntField, ListField, StringField
from pymongo import MongoClient
from tqdm.auto import tqdm, trange

try:
    import core.book as book_
    import core.chapter as chapter_
    import core.endofbook as eob_
    import core.myaml as myaml
    import core.section as section_
    import core.old_title as titlepage_
    from core.atlas import BASE, sg
    from core.book import Book
    from core.log import errwrap, log
except ImportError:
    import book as book_
    import chapter as chapter_
    import endofbook as eob_
    import myaml
    import section as section_
    import titlepage as titlepage_
    from atlas import BASE, sg
    from book import Book
    from log import errwrap, log
#> End of Imports

load_dotenv("../.env")
URI = os.environ.get("MAKE_SUPERGENE")
log.debug(f"MongoDB URI: {URI}")

@errwrap(entry=False, exit=False)
def sg(database: str = "supergene", test: bool=False):
    """
    Custom Connection function to connect to MongoDB Database

    Args:
        `database` (Optional[str]):
            The alternative database you would like to connect to. Default is 'make-supergene'.
    """
    disconnect_all()
    URI = os.environ.get('supergene')
    if test:
        log.info(f"URI: {URI}")
    try:
        connect(database, host=URI)
        if test:
            log.info(f"Connected to MongoDB!")
    except ConnectionError as ce:
        log.error(f"Connection Error: {ce}")
        raise ce
    except Exception as e:
        log.warning(f"Unable to Connect to MongoDB. Error {e}")
        raise e

@errwrap(entry=False, exit=False)
def generate_root():
    if platform() == "Linux":
        ROOT = "home"
    else:
        ROOT = "Users"  # < Mac
    return ROOT


ROOT = generate_root()
BASE = f"/{ROOT}/maxludden/dev/py/supergene"
BOOKS = f"{BASE}/books"


@errwrap()
def generate_book_dir(book: int):
    book_str = str(book).zfill(2)
    return f"book{book_str}"


@errwrap()
def generate_book_path(book: int):
    book_dir = generate_book_path(book)
    return f"{BOOKS}/{book_dir}"


class Default(Document):
    book = IntField(min_value = 1, max_value = 10)
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
    meta = {'collection': 'default'}
    
# sg()
# log.info(f"Count: {str(Default.objects().count())}")
# for x, doc in tqdm(Default.objects().order_by('book'), unit="books"):
#     book = int(doc.book)
#     log.info(f"Book: {book}")
