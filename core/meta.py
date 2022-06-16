# core/meta.py
from mongoengine import Document
from mongoengine.fields import IntField, StringField
from tqdm.auto import tqdm

from core.atlas import ROOT, errwrap, max_title, sg
from core.book import Book
from core.log import log


class Meta(Document):
    book = IntField()
    title = StringField()
    filename = StringField()
    filepath = StringField()
    text = StringField()
    
@errwrap()
def generate_filename(book: int):
    '''
    Generate the filename for the given book's metadata.

    Args:
        `book` (int):
            The given book.

    Returns:
        `filename` (str): 
            The filename for the given book's metadata.
    '''
    #> Generate Filename
    filename =  f'meta{book}.yaml'
    
    #> Update filename in MongoDB
    sg()
    for doc in Meta.objects():
        doc.filename = filename
        doc.save()
        
    return filename

@errwrap()
def get_filename(book: int):
    '''
    Retrieve the given book's meta's filename from MongoDB.

    Args:
        `book` (int):
            The given book

    Returns:
        `filename` (str): 
            The filename for the given book's metadata.
    '''
    sg()
    for doc in Meta.objects(book=book):
        return doc.filename

@errwrap()
def generate_filepath(book: int):
    '''
    Generate filepath for the given book's metadata.

    Args:
        `book` (int):
            The given book.

    Returns:
        `filepath` (str): 
            The filepath for the given book's metadata.
    '''
    #> Generate filepath
    filename = generate_filename(book)
    book_dir = str(book).zfill(2)
    filepath = f"/{ROOT}/maxludden/dev/py/superforge/books"
    filepath = f"{filepath}/book{book_dir}/html/{filename}"
    
    #> Update Filepath in MongoDB
    sg()
    for doc in Meta.objects():
        doc.filepath = filepath
        doc.save()
    return filepath

@errwrap()
def get_filepath(book: int):
    '''
    Retrieve the filepath for the given book's metadata from MongoDB.

    Args:
        `book` (int):
            The given book.
            
    Returns:
        `md_path` (str):
            The filepath of the given book's metadata.
    '''
    sg()
    for doc in Meta.objects(book=book):
        return doc.filepath
    
@errwrap()
def get_title(book: int):
    '''
    Retrieve the given book's title from MongoDB.

    Args:
        `book` (int):
            The given book.
            
    Return:
        `title` (str):
            The title of the given book.
    '''
    #> Retrieve title from Book Collection
    sg()
    for doc in Book.objects():
        title = max_title(doc.title)
    
    #> Update title in MongoDB
    for doc in Meta.objects():
        doc.title = title
        doc.save()
    
    return title

@errwrap()
def generate_text(book: int):
    '''
    Generate the text for the given book's metadata.

    Args:
        `book` (int):
            The given book.
    
    Return:
        `text` (str):
            The given book's metadata's text.
    '''
    #> Retrieve Components from MongoDB
    author = 'Twelve Winged Dark Seraphim'
    sg()
    for doc in Meta.objects():
        #> Generate Text
        text = f"---\ntitle: {doc.title}"
        text = f"{text}\nauthor: {author}"
        text = f"{text}\n..."
        
        #> Save text to MongoDB
        doc.text = text
        doc.save()
        
        #> Write Text to Disk
        with open (doc.filepath, 'w') as outfile:
            outfile.write(text)
            
        return text

@errwrap()
def create_meta():
    '''
    Create the metadata files for each book.
    '''
    sg()
    #> Generate new_meta parameters from Book.
    for doc in tqdm(Book.objects(), unit="book", desc="Creating Metadata"):
        book = doc.book
        title = doc.title
        book_dir = str(book).zfill(2)
        filename = f"meta{book}.yaml"
        filepath = "/Users/maxludden/dev/py/superforge/books/"
        filepath = f"{filepath}book{book_dir}/html/{filename}"
        author = 'Twelve Winged Dark Seraphim'
        text = f"---\ntitle: {title}"
        text = f"{text}\nauthor: {author}"
        text = f"{text}\n..."
        
        #> reconnect to make supergene to add new_meta
        sg()
        new_meta = Meta(
            book = book,
            title = title,
            filename = filename,
            filepath = filepath,
            text = text
        )
        new_meta.save()
        log.info(f'Added metadata for Book {book}.')

@errwrap()
def write_meta(book: int):
    '''
    Retrieve the metadata text of the given book from MongoDB and write it to disk.

    Args:
        `book` (int):
            The given book.
    '''
    sg()
    for doc in tqdm(Meta.objects(book=book), unit="book", desc="Writing Metadata"):
        log.debug(f"Accessed the Metadata for Book {doc.book}.")
        with open(doc.filepath, 'w') as outfile:
            outfile.write(doc.text)
            log.debug(f"Wrote Book {doc.book}'s Metadata to Disk.")

@errwrap()
def write_metadata():
    books = range(1,11)
    for book in tqdm(books, unit=book, desc="Writing Metadata"):
        write_meta(book)