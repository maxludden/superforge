# supergene/core/endofbook.py

import sys
from subprocess import run
from json import load, dump
from tqdm.auto import tqdm

from dotenv import load_dotenv
from mongoengine import Document
from mongoengine.fields import IntField, StringField
from num2words import num2words

from core.book import Book
from core.atlas import max_title, sg, ROOT
from core.log import log, errwrap

load_dotenv()


#.#########################################
#.                                        #
#.  888'Y88              888              #
#.  888 ,'Y 888 8e   e88 888              #
#.  888C8   888 88b d888 888              #
#.  888 ",d 888 888 Y888 888              #
#.  888,d88 888 888  "88 888              #
#.                                        #
#.                                        #
#.             dP,e,                      #
#.   e88 88e   8b "                       #
#.  d888 888b 888888                      #
#.  Y888 888P  888                        #
#.   "88 88"   888                        #
#.                                        #
#.                                        #
#.  888 88b,                     888      #
#.  888 88P'  e88 88e   e88 88e  888 ee   #
#.  888 8K   d888 888b d888 888b 888 P    #
#.  888 88b, Y888 888P Y888 888P 888 b    #
#.  888 88P'  "88 88"   "88 88"  888 8b   #
#.                                        #
#.#########################################


# . EndOfBook Class
class EndOfBook(Document):
    
    book = IntField(Required=True, unique=True)
    book_word = StringField()
    title = StringField(Required=True, max_length=500)
    text = StringField()
    filename = StringField()
    mmd_path = StringField()
    html_path = StringField()
    mmd = StringField()
    html = StringField()
    meta = {
        'collection': 'endofbook'
    }


@errwrap()
def get_book_word(book: int):
    """Retrieves the written represintation to the given book."""
    book_word = num2words(book).capitalize()
    return book_word


@errwrap()
def get_title(book: int):
    """Retrieves the title of the given book."""
    sg()
    for doc in Book.objects(book=book):
        return max_title(doc.title)

@errwrap()
def get_next_book(book: int):
    next_book = book + 1
    return next_book


@errwrap()
def get_next_book_word(book: int):
    next_book_word = num2words(book + 1).capitalize()
    return next_book_word


@errwrap()
def get_next_title(book: int):
    next_book = book + 1
    next_title = get_title(next_book)
    return next_title


@errwrap()
def get_text(book: int):
    """Retrieves the text for the last page of the given book.
    
    Args:
        `book` (int):
            The given EndOfBook's Book.
    """
    if book < 10:
        book_word = get_book_word(book)
        next_book_word = get_next_book_word(book)
        next_title = get_next_title(book)
        
        text = f"#### The End of Book {book_word}"
        text = f"{text}\n##### The story continues in Book {next_book_word}:"
        text = f"{text}\n#### {next_title}\n"
    elif book == 10:
        text = f"End of the Supergene's Last Book."
    else:
        error = f"Invalid input to endofbook.get_text: {book}."
        log.error(error)
        sys.exit(error)


@errwrap()
def get_filename(book: int):
    """Generates the filename of the given book (without extension)."""
    book = str(book).zfill(2)
    return f"endofbook-{book}"


@errwrap()
def get_mmd_path(book: int):
    """Generates the filepath for mmd of the given book's last page.
    
    Args:
        `book` (int):
            The book of the given last page.
    
    Returns:
        `html_path (int):
            The filepath of the given last pages multimarkdown.
    """
    base = "/Users/maxludden/dev/py/supergene/books/"
    book = str(book).zfill(2)
    mmd_path = f"{base}book{book}/mmd/endofbook-{book}.mmd"
    return mmd_path
    
    
@errwrap()
def get_html_path(book: int):
    """Generates the filepath for html of the given book's last page.
    
    Args:
        `book` (int):
            The book of the given last page.
    
    Returns:
        `html_path (int):
            The filepath of the given last pages HTML.
    """
    base = "/Users/maxludden/dev/py/supergene/books/"
    book = str(book).zfill(2)
    html_path = f"{base}book{book}/html/endofbook-{book}.html"
    return html_path


@errwrap()
def get_mmd_text(book: int):
    """Generates the text for the given book's last page.

    Args:
        book (int): The book of the give last page.

    Returns:
        str: The give last page's multimarkdown text.
    """
    if book < 10:
        next_book_word = get_next_book_word(book)
        next_title = get_next_title(book)
        text = f"##### The Story Continues in Book {next_book_word}"
        text = f"{text}\n#### {next_title}..."
        
    elif book == 10:
        text = f"##### The Final Book of Supergene"
        text = f"{text}\n ### The End"
        
    else:
        error = f"Invalid input to endofbook.make_mmd: {book}."
        log.error(error)
        sys.exit(error)
        
    return text
    
    
@errwrap()
def get_mmd(book: int, title: str, book_word: str, mmd_path: str):
    """Generates the multimarkdown string for the given books last page. Saved the MMD to MongoDB and to Disk.
    
    Args:
        `book` (int):
            The last page's book.
        
        `title` (str):
            The title of the last page's book.
            
        `book_word` (str):
            The word form of the last page's book.
            
        `mmd_path` (str):
            The last page's multimarkdown's filepath.
            
    Returns:
        'mmd' (str):
            The multimarkdown for the given book's last page.
    """
    log.debug(f"Accessed Book {book}'s EndOfBook in MongoDB.")
    meta = f"Title: {title}\n"
    meta = f"{meta}Book: {book}\n"
    meta = f"{meta}viewport: width=device-width\n"
    meta = f"{meta}CSS: ../Styles/style.css\n\n"
    log.debug(f"Generated EndOfBook's Metadata.")
    
    atx = f"## {title}\n"
    atx = f"{atx}### End of Book {book_word}\n"
    img = f'<figure>\n\t<img src="../Images/gem.gif" alt="gem" id="gem" width="240" height="120" />\n</figure>'
    atx = f"{atx}{img}\n\n"
    log.debug(f"Generated EndOfBook's ATX Headings.")
    
    text = get_mmd_text(book)
        
    log.debug(f"Generated EndOfBook's Text.")
    mmd = f"{meta}{atx}{text}\n"
    log.debug(f"Concatenated Book {book}'s EndOfBook's Parts.")
    # doc.mmd = mmd
    # doc.save()
    #log.debug(f"Saved Book {book}'s EndOfBook's Mulitmarkdown to MongoDB.")
    with open (mmd_path, 'w') as outfile:
        outfile.write(mmd)
        log.debug(f"Saved Book {book}'s EndOfBook's Mulitmarkdown to Disk.")

    return mmd


@errwrap()
def make_html(book: int, mmd_path: str, html_path: str):
    """Generates the HTML from the given book's EndOFBook's MMD. Saves the HTML string to MongoDB and to Disk.

    Args:
        `book` (int):
            The last page's book.
        
        `title` (str):
            The title of the last page's book.
            
        `book_word` (str):
            The word form of the last page's book.
            
        `mmd_path` (str):
            The last page's multimarkdown's filepath.
            
    Returns:
        'html' (str):
            The HTML for the given book's last page.
    
    """
    
    sg()

    mmd_cmd = [
        "multimarkdown", "-f", "--nolabels", "-o", f"{html_path}", f"{mmd_path}"
    ]
    log.debug(f"MMD: {mmd_path}")
    log.debug(f"HTML: {html_path}")
    log.debug(f"Multitmarkdown Command: {mmd_cmd}")
    try:
        result = run(mmd_cmd)
        if result.returncode == 0:
            log.debug("Converted Book {book}'s EndOfBook's to HTML and saved it to disk.")
    except OSError as ose:
        log.error(ose, traceback=True)
        sys.exit(
            f"OS Error occured in the proccess of creating HTML for Book {book}'s Titlepage.")
    except Exception as e:
        log.error(e, Traceback=True)
        sys.exit(
            f"Error occured in the proccess of creating HTML for Book {book}'s Titlepage")

    with open(html_path, 'r') as infile:
        html = infile.read()

    return html


@errwrap()
def make_endofbooks():
    sg()
    for doc in tqdm(EndOfBook.objects(), unit="books", desc="eobs"):
        book = doc.book
        with open (doc.mmd_path, 'w') as outfile:
            outfile.write(doc.mmd)
        log.debug("Wrote Book {book}'s EndOfBook's multimarkdown to disk.")
        with open (doc.html_path, 'w') as outfile:
            outfile.write(doc.html)
        log.debug("rote Book {book}'s EndOfBook's HTML to disk.")
        