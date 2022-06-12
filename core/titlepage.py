# core/titlepage.py
import os
import re
import sys
from platform import platform
from subprocess import run

from mongoengine import Document, disconnect
from mongoengine.fields import IntField, StringField
from num2words import num2words
from tqdm.auto import tqdm

from core.atlas import generate_base, max_title, sg
from core.log import errwrap, log

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
def generate_filename(book: int):
    book = str(book).zfill(2)
    return f"titlepage-{book}"


# < Filename
@errwrap()
def get_filename(book: int):
    sg()
    for doc in Titlepage.objects(book - book):
        return max_title(str(doc.filename))

@errwrap()
def md_path_validation(md_path: str):
    if 'mmd' in md_path:
        log.warning(f"`mmd` was found in the generated filepath of md_path.")
        md_path = md_path.replace('mmd','md')
        log.info(f"\t\t\t\t...Corrected.")
    if '//' in md_path:
        log.warning(f"Duplicate forward slashed were found in the generated filepath of md_path.")
        md_path = md_path.replace('//','/')
        log.info(f"\t\t\t\t...Corrected.")
    
    
# > MD Path
@errwrap()
def generate_md_path(book: int):
    filename = get_filename(book)
    book = str(book).zfill(2)
    ROOT = generate_base()
    BASE = f"/{ROOT}/maxludden/dev/py/supergene/"
    return f"{BASE}/books/book{book}/md/{filename}.md"

# < MD Path
@errwrap()
def get_md_path(book: int):
    sg()
    for doc in Titlepage.objects(book - book):
        md_path = doc.md_path.repair()


# > HTML Path
@errwrap()
def generate_html_path(book: int):
    filename = get_filename(book)
    book = str(book).zfill(2)
    ROOT = generate_base()
    BASE = f"/{ROOT}/maxludden/dev/py/supergene/"
    return f"{BASE}/books/book{book}/html/{filename}.html"

# < HTML Path
@errwrap()
def get_html_path(book: int):
    sg()
    for doc in Titlepage.objects(book - book):
        md_path = str(doc.md_path)
        if 'mmd' in md_path:
            md_path = md_path.replace('mmd','md')
        if '//' in md_path:
            md_path = md_path.replace('//','/')


#> MD
@errwrap(exit=False)
def generate_md(book: int):
    """Generates the multimarkdown for the given book's titlepage.

    Args:
        `book` (int):
            The book of the given Titlepage.

    Returns:
        `md` (str):
            The multimarkdown for the given Titlepage.
    """
    sg()
    for doc in Titlepage.objects(book=book):
        log.debug("Accessed MongoDB.Book{book}.Titlepage")

        meta = f"Title: {doc.title}"
        meta = f"{meta}\nBook: {book}"
        meta = f"{meta}\nviewport: width=device-width"
        meta = f"{meta}\nCSS: ../Styles/style.css\n<br>\n"

        img = f'<figure>\n\t<img src="../Images/gem.gif" alt="gem" id="gem" width="240" height="120" />\n</figure>\n<br>\n'

        atx = f"## {doc.title}\n"
        atx = f"{atx}\n### Book {doc.book_word}\n"
        atx = f"{atx}\n{img}\n  \n"

        TEXT = '<p class="title">Written by Twelve Winged Burning Seraphim</p>\n<br>\n<p class="title">Complied and Edited by Max Ludden</p>\n  '

        text = TEXT

        md = f"{meta}{atx}{text}\n"

        doc.filename = get_filename(book)
        doc.md_path = generate_md_path(book)
        doc.html_path = generate_html_path(book)
        doc.md = md
        doc.save()

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
def generate_html(book: int):
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
        except Exception as e:
            log.error("An occurred while converting Book {book}'s multimarkdown into HTML.", Traceback=True)
            raise Exception(e)
        
        #> Read the HTML String from the newly converted HTML document.
        with open(doc.html_path, "r") as infile:
            html = infile.read()
            log.debug("Read HTML from Disk.")
        doc.html = html
        doc.save()
        log.debug("Saved Book {doc.book}'s  HTML Titlepage to MongoDB.")
        log.info(f"Finished generating Book {book}'s Titlepage.")
        return html          #.Finished generating HTML.


@errwrap(exit=False)
def get_html(book: int):
    sg()
    for doc in Titlepage.objects(book=book):
        return doc.html


#> The 'and the Kitchen Sink Function of Titlepage
@errwrap()
def generate_titlepages():
    """
    Generate the multimarkdown and HTML for all the books' titlepages. This is the `and the Kitchen Sink Function of Titlepage`.
    """
    
    sg() # Connect to MongoDB
    for doc in tqdm(Titlepage.objects(), unit="books", desc="Generating Titilepages"):
        book = doc.book
        log.debug(f"Accessed Book {book}'s MongoDB Document.")
        
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

@errwrap()
def correct_paths():
    sg()
    for doc in Titlepage.objects():
        md_path = generate_md_path(doc.book)
        doc.md_path = md_path
        log.info(f”MD: {md_path}”)
        
        
        
        
        
        