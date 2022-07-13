# core/epubmeta.py
from errno import EOVERFLOW
from pathlib import Path

from mongoengine import Document
from mongoengine.fields import IntField, StringField
from num2words import num2words
from tqdm.auto import tqdm,trange

try:
  from core.atlas import BASE, errwrap, max_title, sg
  from core.book import Book
  from core.log import log
  import core.myaml as myaml
except ImportError:
  from atlas import BASE, errwrap, max_title, sg
  from book import Book
  from log import errwrap, log
  import myaml


class Epubmeta(Document):
    book = IntField(unique=True, required=True)
    book_word = StringField(max_length=25)
    title = StringField()
    cover_path = StringField()
    filename = StringField()
    html_path = StringField()
    filepath = StringField()
    text = StringField()
    meta = {'collection': 'epubmetadata'}
    
@errwrap()
def generate_filename(book: int, save: bool = False):
    '''
    Generate the filename for the given book's Epub metadata.
    
    Args:
        `book` (int):
            The given book.
        `save` (bool):
            Whether to save the filename to MongoDB.
    
    Returns:
        `filename` (str): 
            The filename for the given book's Epub metadata.
    '''
    #> Generate Filename
    filename =  f'epub-meta{book}.yaml'
    
    #> Update filename in MongoDB
    if save:
        sg()
        for doc in Epubmeta.objects():
            doc.filename = filename
            doc.save()
            
    return filename
    
@errwrap()
def get_filename(book: int):
    '''
    Retrieve the given book's Epub metadata's filename from MongoDB.
    
    Args:
        `book` (int):
            The given book
    returns:
        `filename` (str):
            The given book's Epub metadata's filename.
    '''
    sg()
    for doc in Epubmeta.objects(book=book):
        return doc.filename
    
    
@errwrap()
def generate_filepath(book: int, save: bool = False):
    '''
    Generate the filepath for the given book's Epub metadata.
    
    Args:
        `book` (int):
            The given book
    returns:
        `filepath` (str):
            The filepath for the given book's Epub metadata.
    '''
    book_str = str(book).zfill(2)
    filepath = f"{BASE}/book{book_str}/html/epub-meta{book}.yaml"
    log.debug(f"Generated Book {book}' Epub metadata's filepath: \n{filepath}")
    if save:
        sg()
        for doc in Epubmeta.objects(book=book):
            doc.filepath = filepath
            doc.save()
             
    return filepath


def generate_html_path(book: int, save: bool = False):
    '''
    Generate the html path for the given book's Epub metadata.
    
    Args:
        `book` (int):
            The given book
    returns:
        `html_path` (str):
            The html path for the given book's Epub metadata.
    '''
    book_str = str(book).zfill(2)
    html_path = f"{BASE}/book{book_str}/html/epub-meta{book}.html"
    log.debug(f"Generated Book {book}' Epub metadata's html path: \n{html_path}")
    if save:
        sg()
        for doc in Epubmeta.objects(book=book):
            doc.html_path = html_path
            doc.save()
    return html_path

@errwrap()
def get_filepath(book: int):
    '''
    Retrieve the given book's Epub metadata's filepath from MongoDB.
    
    Args:
        `book` (int):
            The given book
    
    Returns:
        `filepath` (str):
            The given book's Epub metadata's filepath.
    '''
    sg()
    for doc in Epubmeta.objects(book=book):
        return doc.filepath

   
def get_html_path(book: int):
    '''
    Retrieve the given book's Epub metadata's html path from MongoDB.
    
    Args:
        `book` (int):
            The given book
            
    Returns:
        `html_path` (str):
            The given book's Epub metadata's html path.
    '''
    sg()
    for doc in Epubmeta.objects(book=book):
        return doc.html_path

@errwrap()
def generate_cover_path(book: int, save: bool = False):
    book_str = str(book).zfill(2)
    cover_path = f"{BASE}/book{book_str}/cover.jpg"
    log.debug(f"Generated Book {book}' Epub metadata's cover path: \n{cover_path}")
    
    if save:
        sg()
        for doc in Epubmeta.objects(book=book):
            doc.cover_path = cover_path
            doc.save()
            log.debug(f"Saved Book {book}'s cover path to MongoDB.")
    
    return cover_path

@errwrap()  
def get_cover_path(book: int):
    '''
    Retrieve the given book's Epub metadata's cover path from MongoDB.
    
    Args:
        `book` (int):
            The given book
            
    Returns:
        `cover_path` (str):
            The given book's Epub metadata's cover path.
    '''
    sg()
    for doc in Epubmeta.objects(book=book):
        return doc.cover_path
    
    
@errwrap()  
def generate_text(book:int, save: bool = False, write: bool = False):
    '''
    _summary_

    Args:
        `book` (int):
            The given book.
        `save` (bool):
            Whether to save the text to MongoDB. Defaults to False.
        `write` (bool):
            Whether to write the text to a file. Defaults to False.
    Returns:
        `text` (str):
            The text for the given book's Epub metadata.
    '''
    #> Generate Text
    text = f"Book {book}'s Epub metadata:\n"
    text += f"\tTitle: {get_title(book)}\n"
    text += f"\tCover Path: {get_cover_path(book)}\n"
    text += f"\tFilename: {get_filename(book)}\n"
    text += f"\tHTML Path: {get_html_path(book)}\n"
    text += f"\tFilepath: {get_filepath(book)}\n"
    log.debug(f"Generated Book {book}' Epub metadata's text: \n{text}")
    if save:
        sg()
        for doc in Epubmeta.objects(book=book):
            title = doc.title
            book_word = doc.book_word
            author = 'Twelve Winged Dark Seraphim'
            cover_path = doc.cover_path
            
