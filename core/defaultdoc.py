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
    import core.myaml as myaml
    import core.section as sect
    import core.titlepage as titlepg
    from core.atlas import BASE, sg
    from core.log import errwrap, log
    log.debug(f"Imported custom modulesfrom core.")
except ImportError:
    # < If run from the core sub-directory
    import book as bk
    import chapter as ch
    import endofbook as eob
    import myaml
    import section as sect
    import titlepage as titlepg
    from atlas import BASE, sg
    from log import errwrap, log
    log.debug(f"Imported custom modules.")


class Defaultdoc(Document):
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
    
    
#> Book Word
@errwrap()
def book_word(book: int, mode: str='post'):
    '''
    Generates, retrieves, or updates the word from the given book.

    Args:
        `book` (int):
            The given book.
            
        `mode` (Optional[str]):
            The mode in which the function is called.

    Returns:
        `book_word` (str): 
            The written version of the given book.
    '''
    match mode:
        case 'post':
            return str(num2words(book)).capitalize()
        
        case 'get':
            sg()
            for doc in Defaultdoc.objects(book=book):
                book_word = str(doc.book_word).capitalize()
            return book_word
            
        case 'patch':
            bword = book_word(book, mode="post")
            sg()
            for doc in Defaultdoc.objects(book=book):
                doc.book_word = bword
                doc.save()
                log.debug(f"Updated Book {book}'s book_word: {bword}")
 
 
#> Cover
@errwrap()
def generate_cover(book: int, save: bool=True):
    '''
    Generate the filename of the given book's coverpage.

    Args:
        `book` (int):
            The given book.

    Returns:
        `cover` (str): 
            The filename of the given book's coverpage.
    '''
    cover =  f"cover{book}.png"
    return cover
        
@errwrap()
def get_cover(book: int):
    '''
    Retrieve the filename fo the given book's coverpage from MongoDB.

    Args:
        `book` (int):
            The given book.
            
    Returns:
        `cover` (str):
            The filename fo the given book's coverpage retrieved from MongoDB.
    '''
    sg()
    for doc in Defaultdoc.objects(book=book):
        return doc.cover

@errwrap()
def patch_cover(book: int):
    '''
    Generate the filename of the the given book's cover page and update it's value in MongoDB.

    Args:
        `book` (int):
            The given book.
            
    Returns:
        `cover` (str):
            The filename of the given book's cover page.
    '''
    cover = generate_cover(book)
    log.debug(f"Updating Book {book}'s cover: {cover}")
    
    sg()
    for doc in Defaultdoc.objects(book=book):
        doc.cover = cover
        doc.save()
        log.debug(f"Saved Book {book}'s updated coverpage to MongoDB.")
    return cover
 
    
#> Cover Path
@errwrap()
def generate_cover_path(book: int):
    '''
    Generate the filepath for the cover page of the given book.

    Args:
        `book` (int):
            The given book.

    Returns:
        `cover_path` (str): 
            The filepath of the cover page from the given book.
    '''
    cover = generate_cover(book)
    book_zfill = str(book).zfill(2)
    book_dir = f"book{book_zfill}"
    return f'{BASE}/books/{book_dir}/Images/{cover}'






sg()
for doc in Defaultdoc.objects():
    pprint(doc)
