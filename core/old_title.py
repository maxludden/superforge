# core/titlepage.py

import os
import re
import sys
from json import dump, load
from platform import platform
from subprocess import run

from mongoengine import Document, disconnect
from mongoengine.fields import IntField, StringField
from num2words import num2words
from tqdm.auto import tqdm, trange
from alive_progress import alive_bar

try:
    from core.atlas import BASE, max_title, sg
    from core.log import errwrap, log
except ImportError:
    from atlas import BASE, max_title, sg
    from log import errwrap, log
    
    
# .####################################################################
# .                                                                   #
# .              88P'888'Y88 ,e,   d8   888                           #
# .              P'  888  'Y  "   d88   888  ,e e,                    #
# .                  888     888 d88888 888 d88 88b                   #
# .                  888     888  888   888 888   ,                   #
# .                  888     888  888   888  "YeeP"                   #
# .                                                                   #
# .                                                                   #
# .                                                                   #
# .     888 88e   ,"Y88b  e88 888  ,e e,      888 88e  Y8b Y888P      #
# .     888 888b "8" 888 d888 888 d88 88b     888 888b  Y8b Y8P       #
# .     888 888P ,ee 888 Y888 888 888   , d8b 888 888P   Y8b Y        #
# .     888 88"  "88 888  "88 888  "YeeP" Y8P 888 88"     888         #
# .     888                ,  88P             888         888         #
# .     888               "8",P"              888         888         #
# .                                                                   #
# .####################################################################


class MMDConversionException(Exception):
    pass

class Titlepage(Document):
    book = IntField(Required=True, unique=True, Indexed=True)
    book_word = StringField()
    title = StringField(Required=True, max_length=500)
    text = StringField()
    filename = StringField()
    md_path = StringField()
    html_path = StringField()
    md = StringField()
    html = StringField()


# > Filename
@errwrap()
def generate_filename(book: int, save: bool = False) -> str:
    '''
    Generate the filename of the given book's Titlepage.

    Args:
        `book` (int):
            The given book.
        `save` (bool):
            Whether to save the filename to MongoDB. Defaults to False.

    Returns:
        `filename` (str): 
            The filename of the given book.
    '''
    book = str(book).zfill(2)
    filename = f'titlepage-{book}.md'
    if save:
        sg()
        for doc in Titlepage.objects(book=book):
            doc.filename = filename
            doc.save()
    
    return filename


# < Filename
@errwrap()
def get_filename(book: int):
    '''
    Retrieve the given book's Titlepage's name from MongoDB.

    Args:
        `book` (int):
            The given book

    Returns:
        `filename` (str): 
            The filename (without extension) of the given Titlepage.
    '''
    sg()
    for doc in Titlepage.objects(book=book):
        return doc.filename
    

#>> MD Path
@errwrap()
def generate_md_path(book: int, save: bool = False) -> str:
    '''
    Generates the filepath for the multimarkdown of the given book's Titlepage.

    Args:
        `book` (int):
            The given book.
        `save` (bool):
            Whether to save the filename to MongoDB. Defaults to False.

    Returns:
        `md_path` (str): 
            The filepath for the given book's Titlepage.
    '''
    book_str = str(book).zfill(2)
    filename = f"titlepage-{book_str}"
    md_path = f"{BASE}/books/book{book_str}/md/{filename}.md"
    if save:
        sg()
        for doc in Titlepage.objects(book=book):
            doc.md_path = md_path
            doc.save()
    return md_path


# > MD Path
@errwrap()
def get_md_path(book: int):
    '''
    Retrieve the filepath for a given book's Titlepage's multimarkdown from MongoDB.

    Args:
        `book` (int):
            The given book.

    Returns:
        `md_path` (str): 
            The filepath for the given multimarkdown file.
    '''
    sg()
    for doc in Titlepage.objects(book=book):
        return md_path


# > HTML Path
@errwrap()
def generate_html_path(book: int, save: bool = False):
    '''
    Generates the filepath for the HTML of the given book's Titlepage.

    Args:
        `book` (int):
            The given book.
        `save` (bool):
            Whether to save the filename to MongoDB. Defaults to False.

    Returns:
        `md_path` (str): 
            The filepath for the given book's Titlepage.
    '''
    filename = get_filename(book)
    book_str = str(book).zfill(2)
    html_path = f"{BASE}/books/book{book_str}/html/{filename}.html"
    if save:
        sg()
        for doc in Titlepage.objects(book=book):
            doc.html_path = html_path
            doc.save()
    return html_path


#>> HTML Path
@errwrap()
def get_html_path(book: int):
    '''
    Retrieve the filepath for a given book's Titlepage's HTML from MongoDB.

    Args:
        `book` (int):
            The given book.

    Returns:
        `md_path` (str): 
            The filepath for the given HTML file.
    '''
    sg()
    for doc in Titlepage.objects(book=book):
        return path_eval(doc.md_path)


#> MD
@errwrap(exit=False)
def generate_md(book: int, save: bool = False, write: bool = False):
    """Generates the multimarkdown for the given book's titlepage.

    Args:
        `book` (int):
            The book of the given Titlepage.
        `save` (bool):
            Whether or not to save the generated multimarkdown to MongoDB.
        `write` (bool):
            Whether or not to write the generated multimarkdown to disk.

    Returns:
        `md` (str):
            The multimarkdown for the given Titlepage.
    """
    sg()
    for doc in Titlepage.objects(book=book):
        log.debug("Accessed MongoDB.Book{book}.Titlepage")

        meta = f"---\nTitle: {doc.title}"
        meta = f"{meta}\nBook: {book}"
        meta = f"{meta}\nviewport: width=device-width"
        meta = f"{meta}\nCSS: ../Styles/style.css\n...\n"

        img = f'<figure>\n\t<img class="titlepage" src="../Images/gem.gif" alt="gem" />\n</figure>\n'

        atx = f'\n# {doc.title}\n'
        atx = f"{atx}\n### Book {doc.book_word}\n"
        atx = f"{atx}\n{img}\n"

        TEXT = '<p class="title">Written by Twelve Winged Dark Seraphim</p>\n<p class="title">Complied and Edited by Max Ludden</p>'

        text = TEXT

        md = f"{meta}{atx}{text}\n"

        doc.filename = get_filename(book)
        log.debug(f"Doc.filename: {doc.filename}")
        doc.md_path = generate_md_path(book)
        log.debug(f"Doc.md_path: {doc.md_path}")
        doc.html_path = generate_html_path(book)
        if save:
            doc.md = md
            doc.save()
        
        if write:
            with open(doc.md_path, "w") as outfile:
                outfile.write(md)
            log.debug(f"Wrote Book {book}'s titlepage to disk and DB.")
    return md

#< MD
@errwrap(exit=False)
def get_md(book: int):
    '''
    Retrieves the multimarkdown for the given chapter from MongoDB.

    Args:
        `book` (int):
            The given book.

    Returns:
        `html` (str): 
            The HTML for the given chapter.
    '''
    sg()
    for doc in Titlepage.objects(book=book):
        return doc.md


#> HTML
@errwrap(exit=False)
def generate_html(book: int, save: bool = False):
    """
    Generates the HTML for a given book's titlepage from its multimarkdown.

    Args:
        `book` (int):
            The given Titlepage's book.
    
    Returns:
        `html` (str):
            The HTML of the given chapter.
    """
    sg() # Connect to MongoDB
    for doc in Titlepage.objects(book=book):
        md_cmd = [
            "multimarkdown",
            "-f",
            "--nolabels",
            "-o",
            f"{doc.html_path}",
            f"{doc.md_path}",
        ]
        log.debug(f"md: {doc.md_path}")
        log.debug(f"HTML: {doc.html_path}")
        log.debug(f"Multitmarkdown Command: {md_cmd}")
        try:
            #> Attempt to use Multimarkdown 6's CLI to convert the multimarkdown into (X)HTML.
            result = run(md_cmd)
            if result.returncode == 0:
                log.debug("Converted Book {book}'s titlepage to HTML.")
        except OSError as ose:
            log.error("An OSError occurred while converting Book {book}'s multimarkdown into HTML.", traceback=True)
            raise OSError(ose)
        except MMDConversionException as e:
            log.error("An occurred while converting Book {book}'s multimarkdown into HTML.", Traceback=True)
            raise MMDConversionException(e)
        
        #> Read the HTML String from the newly converted HTML document.
        with open(doc.html_path, "r") as infile:
            html = infile.read()
            log.debug("Read HTML from Disk.")
            
        if save:
            doc.html = html
            doc.save()
            log.debug(f"Saved Book {book}'s titlepage to MongoDB.")

        log.debug("Saved Book {doc.book}'s  HTML Titlepage to MongoDB.")
        log.info(f"Finished generating Book {book}'s Titlepage.")
        return html          #.Finished generating HTML.


@errwrap(exit=False)
def get_html(book: int):
    '''
    Retrieve the given book's titlepage's html from MongoDB.

    Args:
        `book` (int):
            The given book.

    Returns:
        `html` (str): 
            The HTML of the given book's titlepage.
    '''
    sg()
    for doc in Titlepage.objects(book=book):
        return doc.html


#> The 'and the Kitchen Sink Function of Titlepage
@errwrap()
def generate_titlepages():
    """
    Generate the multimarkdown and HTML for all the books' titlepages. This is the "and the Kitchen Sink Function of Titlepage".
    """
    
    sg() # Connect to MongoDB
    for doc in tqdm(Titlepage.objects(), unit="books", desc="Generating Titilepages"):
        book = doc.book
        log.info(f"Accessed Book {book}'s MongoDB Document.")
        
        #> MD
        book = doc.book
        md = generate_md(book)
        if 'mmd' in md:
            raise ValueError("File: core.titlepage.py\nFunction: make-titlepages\nLine 222\nValueError: The string `mmd` was found in the filepath of Book {book}'s Titlepage. Traceback Error: {e}")
        elif len(md) < 100:
            raise TypeError("File: core.titlepage.py\nFunction: make-titlepages\nLine 227\nType Error: the provided Titlepage was less that 100 Characters long.")
        
        #> HTML
        html = generate_html(book)
        length = len(html)
        if length < 100:
            raise TypeError("File: core.titlepage.py\nFunction: make-titlepages\nLine 235\nType Error: the provided Titlepage was less that 100 Characters long.")
        else:
        
            #> Update MongoDB with the given Titlepage's multimarkdown and HTML.
            doc.md = md
            doc.html = html
            doc.save()
            log.debug(f"Finished generating Book {book}'s Titlepage.")

@errwrap(exit=False)
def html_check():
    '''
    Retrieves the HTML for each book's Titlepage and stores it in `json/html.json`.
    '''
    sg()
    html_dict = {}
    for doc in Titlepage.objects():
        book = doc.book
        log.info(f"Accessed Book {book}'s Titlepage's Document in MongoDB.")
        html_dict[book] = doc.html
        
    with open("/Users/maxludden/dev/py/superforge/json/html.json", 'w') as outfile:
        dump(html_dict, outfile, indent=4)
        
sg()
titlepages = Titlepage.objects.all()
count = len(titlepages)

for doc in Titlepage.objects():
    with alive_bar(count, title='Generating Titlepages') as bar:
        book = doc.book
        generate_filename(book, save=True)
        generate_md_path(book, save=True)
        generate_html_path(book, save=True)
        generate_md(book, save=True, write=True)
        bar.title(f"Generated Book {book}'s Titlepage's MD.")
        generate_html(book, save=True)
        bar.title(f"Generated Book {book}'s Titlepage's HTML.")
        bar()