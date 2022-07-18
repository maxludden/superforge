# core/Metadata.py
from mongoengine import Document
from mongoengine.fields import IntField, StringField
from tqdm.auto import tqdm, trange
from alive_progress import alive_bar

try:
    from core.atlas import BASE, errwrap, max_title, sg
    from core.book import Book
    from core.log import log, errwrap
    import core.myaml as myaml
except:
    from atlas import BASE, max_title, sg
    from book import Book
    from log import errwrap, log
    import myaml


class Metadata(Document):
    book = IntField()
    title = StringField()
    filename = StringField()
    filepath = StringField()
    html_path = StringField()
    text = StringField()
    meta = {'collection': 'metadata'}
    
@errwrap()
def generate_filename(book: int, save: bool = True):
    '''
    Generate the filename for the given book's Metadatadata.

    Args:
        `book` (int):
            The given book.

    Returns:
        `filename` (str): 
            The filename for the given book's Metadatadata.
    '''
    #> Generate Filename
    filename =  f'meta{book}.yml'
    
    #> Update filename in MongoDB
    if save:
        sg()
        for doc in Metadata.objects():
            doc.filename = filename
            doc.save()
        
    return filename

@errwrap()
def get_filename(book: int):
    '''
    Retrieve the given book's Metadata's filename from MongoDB.

    Args:
        `book` (int):
            The given book

    Returns:
        `filename` (str): 
            The filename for the given book's Metadatadata.
    '''
    sg()
    for doc in Metadata.objects(book=book):
        return doc.filename

@errwrap()
def generate_filepath(book: int, save: bool = True):
    '''
    Generate filepath for the given book's Metadatadata.

    Args:
        `book` (int):
            The given book.

    Returns:
        `filepath` (str): 
            The filepath for the given book's Metadatadata.
    '''
    #> Generate filepath
    filename = generate_filename(book)
    book_str = str(book).zfill(2)
    book_dir = f"book{book_str}"
    filepath = f"{BASE}/books/{book_dir}/yaml/{filename}"
    
    #> Update Filepath in MongoDB
    if save:
        sg()
        for doc in Metadata.objects():
            doc.filepath = filepath
            doc.html_path = filepath
            doc.save()
            log.debug(f"Updated Book {book}' Metadata's filepath:\n{filepath}")
    return filepath



@errwrap()
def get_filepath(book: int):
    '''
    Retrieve the filepath for the given book's Metadatadata from MongoDB.

    Args:
        `book` (int):
            The given book.
            
    Returns:
        `md_path` (str):
            The filepath of the given book's Metadatadata.
    '''
    filepath = generate_filepath(book)
    return filepath
    
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
    for doc in Metadata.objects():
        doc.title = title
        doc.save()
    
    return title

@errwrap()
def generate_text(book: int, save: bool = False, write: bool = False):
    '''
    Generate the text for the given book's Metadatadata.

    Args:
        `book` (int):
            The given book.
    
    Return:
        `text` (str):
            The given book's Metadatadata's text.
    '''
    #> Retrieve Components from MongoDB
    author = 'Twelve Winged Dark Seraphim'
    sg()
    for doc in tqdm(Metadata.objects(book=book), unit="books", desc="Generating Metadata"):
        #> Generate Text
        pyobject = {
            "title": doc.title,
            "author": author
        }
        text = myaml.dump(pyobject)
        text = f"---\n{text}..."
        log.debug(f"Generated yaml text for book {book}'s Metadata. \n \n{text}")
        #> Save text to MongoDB
        if save:
            doc.text = text
            doc.save()
        
        #> Write Text to Disk
        if write:
            with open(doc.filepath, 'w') as f:
                f.write(text)
                log.debug(f"Wrote yaml text for book {book}'s Metadata to disk.")
            
        return text

@errwrap()
def create_Metadata():
    '''
    Create the Metadatadata files for each book.
    '''
    sg()
    #> Generate new_Metadata parameters from Book.
    for doc in tqdm(Book.objects(), unit="book", desc="Creating Metadatadata"):
        book = doc.book
        title = doc.title
        book_dir = str(book).zfill(2)
        filename = f"Metadata{book}.yaml"
        filepath = "/Users/maxludden/dev/py/superforge/books/"
        filepath = f"{filepath}book{book_dir}/html/{filename}"
        author = 'Twelve Winged Dark Seraphim'
        text = f"---\ntitle: {title}"
        text = f"{text}\nauthor: {author}"
        text = f"{text}\n..."
        
        #> reconnect to make supergene to add new_Metadata
        sg()
        new_Metadata = Metadata(
            book = book,
            title = title,
            filename = filename,
            filepath = filepath,
            text = text
        )
        new_Metadata.save()
        log.debug(f'Added Metadatadata for Book {book}.')

@errwrap()
def write_Metadata(book: int):
    '''
    Retrieve the Metadatadata text of the given book from MongoDB and write it to disk.

    Args:
        `book` (int):
            The given book.
    '''
    sg()
    for doc in tqdm(Metadata.objects(book=book), unit="book", desc="Writing Metadatadata"):
        log.debug(f"Accessed the Metadatadata for Book {doc.book}.")
        with open(doc.filepath, 'w') as outfile:
            outfile.write(doc.text)
            log.debug(f"Wrote Book {doc.book}'s Metadatadata to Disk.")

@errwrap()
def write_Metadatadata():
    sg()
    for doc in tqdm(Metadata.objects(), unit="book", desc="Writing Metadatadata"):
        write_Metadata(doc.book)
       
with alive_bar(40, title="Ad-hoc Generating Metadata", dual_line=True) as bar: 
    for i in range(1,11):
        bar.text=f"Book {i}: Metadata"
        bar()
        generate_filename(i, save = True)
        log.debug(f"Generated filename for Book {i}'s Metadata.")
        bar()
        filepath = generate_filepath(i, save=True)
        log.debug("Generated filepath for Book {i}'s Metadata.")
        bar()
        bar.text=f"Book {i}: Text"
        log.debug(f"Generated Book {i}'s Filepath.")
        generate_text(i, save=True, write=True)
        bar()