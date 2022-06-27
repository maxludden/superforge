# core/epubmeta.py
from pathlib import Path

from mongoengine import Document
from mongoengine.fields import IntField, StringField
from num2words import num2words
from tqdm.auto import tqdm

try:
  from core.atlas import ROOT, errwrap, max_title, sg
  from core.book import Book
  from core.log import log
except ImportError:
  from atlas import ROOT, errwrap, max_title, sg
  from book import Book
  from log import log, errwrap


class Epubmeta(Document):
    book = IntField(unique=True, required=True)
    book_word = StringField(max_length=25)
    title = StringField()
    cover_path = StringField()
    filename = StringField()
    filepath = StringField()
    text = StringField()
    
TEMPLATE_PATH = Path("yaml/base-docs/epub-meta.yaml")

@errwrap()
def create_epubmeta(book: int):
    '''
    Create a new document in MongoDB for epubmeta for a given book.

    Args:
        `book` (int):
            The given book.
    '''
    #> Retrieve data from Book
    sg()
    for doc in Book.objects(book=book):
        title = max_title(doc.title)
        cover_path = doc.cover_path
    
    #> Filename and path
    filename = f'epub-meta{book}.yaml'
    book_dir = str(book).zfill(2)
    filepath = f'books/book{book_dir}/html/{filename}'
    book_word = num2words(book)
    
    #> Text
    text = f'''title:
- type: main
  text: {title}
- type: subtitle
  text: Book {book_word}
creator:
- role: author
  text: Twelve Winged Dark Seraphim
- role: editor
  text: Max Ludden
stylesheet: 
- style.css
cover-image: {cover_path}
ibooks:
- version: 4.0
- specified-fonts: true
- iphone-orientation-lock: portrait-only
belongs-to-collection: Super Gene
group-position: {book}'''

    #> Creation
    new_epub_meta = Epubmeta(
        book = book,
        book_word = book_word,
        title = title,
        cover_path = cover_path,
        filename = filename,
        filepath = filepath,
        text = text
    )
    new_epub_meta.save()
    log.debug(f"Saved Book {book}'s Epub Metadata in MongoDB.")
    
    #> Write to Disk
    with open (filepath, 'w') as outfile:
        outfile.write(text)
        log.debug(f"Wrote Book {book}'s Epub Metadata to Disk.")
        
    log.info(f"Created Book {book}'s Epub Metadata. Save it to MongoDB and wrote it to disk.")
        
@errwrap()
def create_all_epubmeta():
    '''
    Create and write all books epub metadata to MongoDB and to Disk.
    '''
    books = range(1,11)
    for book in tqdm(books, unit="book", desc="Creating Epub Metadata"):
        create_epubmeta(book)
    
@errwrap()
def update_epubmeta(book: int):
    sg()
    for doc in Epubmeta.objects(book=book):
        book_word = str(num2words(book)).capitalize()
        doc.book_word = book_word
        doc.save()
        
        title = doc.title
        cover_path = doc.cover_path
        filepath = doc.filepath
        text = f'''title:
- type: main
  text: {title}
- type: subtitle
  text: Book {book_word}
creator:
- role: author
  text: Twelve Winged Dark Seraphim
- role: editor
  text: Max Ludden
stylesheet: 
- style.css
cover-image: {cover_path}
ibooks:
- version: 4.0
- specified-fonts: true
- iphone-orientation-lock: portrait-only
belongs-to-collection: Super Gene
group-position: {book}'''
        doc.text = text
        doc.save()
        log.debug(f"Updated Book {book}'s Epub Metadata in MongoDB.")
        
        with open (filepath, 'w') as outfile:
            outfile.write(text)
            log.debug(f"Wrote Book {book}'s updated Epub Meta to Disk.")
        log.info(f"Updated Book {book}'s Epub Metadata.")

@errwrap()
def update_all_epubmeta():
    '''
    Update all books' Epub Metadata
    '''
    books = range(1,11)
    for book in tqdm(books, unit="book", desc="Updating Epub Metadata"):
        update_epubmeta(book)
