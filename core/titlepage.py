# core/titlepage.py
import os
import re
import sys
from subprocess import run

from mongoengine import Document, disconnect
from mongoengine.fields import IntField, StringField
from num2words import num2words
from tqdm.auto import tqdm

from core.atlas import sg
from core.book import Book
from core.log import errwrap, log

TEXT = "#### Written by Twelve Winged Burning Seraphim"
TEXT = f"{TEXT}\n#### Complied and Edited by Max Ludden"

#.####################################################################
#.                                                                   #
#.              88P'888'Y88 ,e,   d8   888                           #
#.              P'  888  'Y  "   d88   888  ,e e,                    #
#.                  888     888 d88888 888 d88 88b                   #
#.                  888     888  888   888 888   ,                   #
#.                  888     888  888   888  "YeeP"                   #
#.                                                                   #
#.                                                                   #
#.                                                                   #
#.     888 88e   ,"Y88b  e88 888  ,e e,      888 88e  Y8b Y888P      #
#.     888 888b "8" 888 d888 888 d88 88b     888 888b  Y8b Y8P       #
#.     888 888P ,ee 888 Y888 888 888   , d8b 888 888P   Y8b Y        #
#.     888 88"  "88 888  "88 888  "YeeP" Y8P 888 88"     888         #
#.     888                ,  88P             888         888         #
#.     888               "8",P"              888         888         #
#.                                                                   #
#.####################################################################


class Titlepage(Document):
    book = IntField(Required=True, unique=True, Indexed=True)
    book_word = StringField()
    title = StringField(Required=True, max_length=500)
    text = StringField(default=f'{TEXT}')
    filename = StringField()
    mmd_path = StringField()
    html_path = StringField()
    mmd = StringField()
    html = StringField()


def get_filename(book: int):
    book = str(book).zfill(2)
    return f"titlepage-{book}"


def get_mmd_path(book: int):
    filename = get_filename(book)
    book = str(book).zfill(2)
    return f"/Users/maxludden/dev/py/supergene/books/book{book}/mmd/{filename}.mmd"


def get_html_path(book: int):
    filename = get_filename(book)
    book = str(book).zfill(2)
    return f"/Users/maxludden//dev/py/supergene/books/book{book}/html/{filename}.html"

@errwrap(exit=False)
def get_mmd(book: int):
    """Generates the multimarkdown for the given book's titlepage.
    
    Args:
        `book` (int):
            The book of the given Titlepage.
            
    Returns:
        mmd (str):
            The multimarkdown for the given Titlepage.
    """
    sg()
    for doc in Titlepage.objects(book=book):
        log.debug("Accessed MongoDB.Book{book}.Titlepage")

        meta = f"Title: {doc.title}"
        meta = f"{meta}\nBook: {book}"
        meta = f"{meta}\nviewport: width=device-width"
        meta = f"{meta}\nCSS: ../Styles/style.css\n\n"

        atx = f"## {doc.title}\n"
        atx = f"{atx}\n### Book {doc.book_word}\n"
        img = f'<figure>\n\n<img src="../Images/gem.gif" alt="gem" id="gem" width="240" height="120" />\n\n</figure>'
        atx = f"{atx}\n{img}\n\n"

        text = TEXT

        mmd = f"{meta}{atx}{text}\n"

        doc.filename = get_filename(book)
        doc.mmd_path = get_mmd_path(book)
        doc.html_path = get_html_path(book)
        doc.mmd = mmd
        doc.save()

        with open(doc.mmd_path, 'w') as outfile:
            outfile.write(mmd)
        log.debug(f"Wrote Book {book}'s titlepage to disk and DB.")
    return mmd


@errwrap()
def validate_mmd(book: int, force: bool = False):
    """
    Validate the given titlepage's mmd in both MongoDB as well as saved to disk.
    
    Args:
        `book` (int):
            The book of the given Titlepage.
            
        `force` (Optional[bool]):
            If true, forces the (re)creation of the given Book's Titlepage multimarkdown.
            
    """
    
    sg()
    for doc in Titlepage.objects(book=book):
        
        if force:
            mmd = get_mmd(doc.book)
            with open(doc.mmd_path, 'w') as mmd_file:
                mmd_file.write(mmd)
                log.debug(
                    f"Generated mmd for the Book {doc.book}'s Titlepage and saved it to disk.")
            doc.mmd = mmd
            doc.save()
            log.debug(f"Saved generated mmd to MongoDB.")
            return doc

        if doc.mmd == "":
            with open(doc.mmd_path, 'r+') as mmd_file:
                mmd = mmd_file.read()
                if not mmd:
                    log.debug(f"Generating mmd...")
                    mmd = get_mmd(doc.book)
                    mmd_file.write(mmd)
                    doc.mmd = mmd
                    doc.save()
                    log.debug("Generated")
                    return doc

                if mmd != doc.mmd:
                    log.debug(
                        f"The mmd written to disk does not match what's in MongoDB. Regenerating MMD for both...")
                    mmd = get_mmd(doc.book)
                    mmd_file.write(mmd)
                    doc.mmd = mmd
                    doc.save()
                    log.debug(
                        f"Generated mmd. Saved to MongoDB and wrote it to disk.")
                    return doc

        log.debug(f"Validated Book {doc.book}'s Titlepage's MMD.")

@errwrap()
def validate_values(book: int):
    """
    Validates Titlepage's metadata and corrects or adds missing or invalid values.
    
    Args:
        `book` (int):
            The book of the given Title
    """
    
    log.info(f"Validating Book {doc.book}'s Metadata")
    update = False
    
    log.debug(f"Book {doc.book}'s book_word: {doc.book_word}")
    if doc.book_word == "":
        doc.book_word = num2words(doc.book)
        log.debug(f"Generated book_word: {doc.book_word}")
        update = True
    
    log.debug(f"Book {doc.book}'s Title: {doc.title}")
    if doc.title == "":
        sg()
        for doc in Book.objects(book=doc.book):
            doc.title = max.title(doc.title)
        log.debug(
            f"Retrieving Book {doc.book}'s title from MongoDB: {doc.title}")
        update = True

    log.debug(f"Book {doc.book}'s filename: {doc.filename}")
    if (doc.filename == "") | ('.' in doc.filename):
        doc.filename == get_filename(doc.book)
        log.debug(
            f"Generated Book {doc.book}'s titlepage's filename: {doc.filename}")
        update = True

    log.debug(f"Book")
    if doc.mmd_path == "":
        doc.mmd_path = get_mmd_path(doc.book)
        log.debug(
            f"Generated Book {doc.book}'s titlepage's mmd_path: {doc.mmd_path}")
        update = True

    if doc.html_path == "":
        doc.html_path = get_html_path(doc.book)
        log.debug(
            f"Generated Book {doc.book}'s titlepage's html_path: {doc.html_path}")
        update = True

    if update:
        doc.save()
        log.info(f"Updated Book {doc.book}'s Titlepage's metadata.")
    else:
        log.info(f"Validated Book {doc.book}'s Titlepage's metadata.")


@errwrap()
def validate_html(book: int, force: bool = False):
    """
    Validate the given titlepages's html in both MongoDB as well as saved to disk.
    """
    sg()
    for doc in Titlepage.objects(book=book):
        if force:
            log.info(
                f"Forcing the generation of HTML for Book {doc.book}'s titlepage.")
            doc.html = make_html(doc.book)
            doc.save
            print(f"Titlepage's html:\n\n{doc.html}")
            log.info(f"Generated the HTML for the book {doc.book}'s titlepage.")

        if doc.html == "":
            log.debug(f"HTML not found in MongoDB. Generating HTML...")
            doc.html = make_html(doc.book)
            doc.save()
            log.debug(f"Generated the HTML for the book {doc.book}'s titlepage.")
        else:
            log.debug(f"Validated Book {doc.book}'s titlepage's HTML.")



@errwrap(exit=False)
def make_html(book: int):
    """
    Generate the HTML for a given book's titlepage from it's multimarkdown.
    
    Args:
        `book` (int):
            The given Titlepage's book.
    """

    sg()
    for doc in Titlepage.objects(book=book):
        mmd_cmd = [
            "multimarkdown", "-f", "--nolabels", "-o", f"{doc.html_path}", f"{doc.mmd_path}"
        ]
        log.debug(f"MMD: {doc.mmd_path}")
        log.debug(f"HTML: {doc.html_path}")
        log.debug(f"Multitmarkdown Command: {mmd_cmd}")
        try:
            result = run(mmd_cmd)
            if result.returncode == 0:
                log.debug("Converted Book {book}'s titlepage to HTML.")
        except OSError as ose:
            log.error(ose, traceback=True)
            sys.exit(
                f"OS Error occured in the proccess of creating HTML for Book {doc.book}'s Titlepage.")
        except Exception as e:
            log.error(e, Traceback=True)
            sys.exit(
                f"Error occured in the proccess of creating HTML for Book {doc.book}'s Titlepage")

        with open(doc.html_path, 'r') as infile:
            html = infile.read()
        doc.html = html
        doc.save()
        log.info("Saved Book {doc.book}'s Titlepage's HTML to MongoDB.")

        return html

@errwrap()
def make_titlepages():
    """Generate the multimarkdown and HTML for all the books' titlepages.
    """
    sg()
    for doc in tqdm(Titlepage.objects(), unit="books", desc="Generating Titilepages"):
        book = doc.book
        mmd = get_mmd(book)
        html = make_html(book)
        
        
