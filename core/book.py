# #core/book.py
from subprocess import run

from mongoengine import Document
from mongoengine.fields import IntField, ListField, StringField, UUIDField

from core.atlas import BASE, max_title, sg
from core.log import errwrap, log

# . ############################################################### . #
# .                                                                 . #
# .                                                                 . #
# .                                                                 . #
# .  888                          888                               . #
# .  888 88e   e88 88e   e88 88e  888 ee     888 88e  Y8b Y888P     . #
# .  888 888b d888 888b d888 888b 888 P      888 888b  Y8b Y8P      . #
# .  888 888P Y888 888P Y888 888P 888 b  d8b 888 888P   Y8b Y       . #
# .  888 88"   "88 88"   "88 88"  888 8b Y8P 888 88"     888        . #
# .                                          888         888        . #
# .                                          888         888        . #
# .                                                                 . #
# . ############################################################### . #


class Book (Document):
    book = IntField(Required=True, unique=True, indexed=True)
    book_word = StringField(Required=True)
    title = StringField(Required=True, max_length=500)
    chapters = ListField(IntField())
    cover = StringField()
    cover_path = StringField()
    default = StringField()
    start = IntField(min_value=1)
    end = IntField(max_value=3463)
    output = StringField()
    uuid = UUIDField(binary=False)


# > Declaring Static Variables
written: str = "Written by Twelve Winged Burning Seraphim"
edited: str = "Complied and Edited by Max Ludden"
TEXT = f'<p class="title">{written}</p>\n<p class="title">{edited}</p>'



#.
#.   ____                      ____                  
#.  / ___|_____   _____ _ __  |  _ \ __ _  __ _  ___ 
#. | |   / _ \ \ / / _ \ '__| | |_) / _` |/ _` |/ _ \
#. | |__| (_) \ V /  __/ |    |  __/ (_| | (_| |  __/
#.  \____\___/ \_/ \___|_|    |_|   \__,_|\__, |\___|
#.                                        |___/     
#.


class Coverpage(Document):
    book = IntField(Required=True, unique=True, indexed=True)
    filename = StringField()
    md_path = StringField()
    html_path = StringField()
    md = StringField()
    html = StringField()
    meta = {
        'collection': 'coverpage'
    }


#> Filename
@errwrap()
def generate_filename(book: int):
    '''
    Generate the filename of the given book's cover page.

    Args:
        `book` (int):
            The given book

    Returns:
        `filename` (str): 
            The filename of the given book's cover page.
    '''
    return f'cover{book}'

@errwrap()
def get_filename(book: int):
    '''
    Retrieve the filename of the given book's cover page from MongoDB.

    Args:
        `book` (int):
            The given book.

    Returns:
        `filename` (str): 
            The filename of the given book's cover page.
    '''
    sg()
    for doc in Coverpage.objects(book=book):
        return doc.filename


#> MD Path
@errwrap()
def generate_md_path(book: int):
    '''
    Generate the md path for the given book's cover page.

    Args:
        `book` (int):
            The given book.

    Returns:
        `html_path` (_type_): 
            The md path for the given book's cover page.
    '''
    book_dir = str(book).zfill(2)
    filename = generate_filename(book)
    return f'{BASE}/books/book{book_dir}/md/{filename}.md'

@errwrap()
def get_md_path(book: int):
    '''
    Retrieve the path of the given book's coverpage from MongoDB.

    Args:
        `book` (int):
            The given book.

    Returns:
        `md_path` (str): 
            The path of the given book's coverpage from MongoDB.
    '''
    sg()
    for doc in Coverpage.objects(book=book):
        return doc.md_path


#> HTML Path
@errwrap()
def generate_html_path(book: int):
    '''
    Generate the html path for the given book's cover page.

    Args:
        `book` (int):
            The given book.

    Returns:
        `html_path` (_type_): 
            The html path for the given book's cover page.
    '''
    book_dir = str(book).zfill(2)
    filename = generate_filename(book)
    return f'{BASE}/books/book{book_dir}/html/{filename}.html'

@errwrap()
def get_html_path(book: int):
    '''
    Retrieve the html path for the given book's cover page from MongoDB.

    Args:
        `book` (int):
            The given book.

    Returns:
        `html_path` (_type_): 
            The html path for the given book's cover page.
    '''
    sg()
    for doc in Coverpage.objects(book=book):
        return doc.html_path


#> MD
@errwrap()
def generate_md(book: int):
    '''
    Generate the multimarkdown for the given book's cover page.

    Args:
        `book` (int):
            The given book.

    Returns:
        `md` (str): 
            The multimarkdown for the given book's cover page
    '''
    sg()
    cover_path = ""
    for doc in Book.objects(book=book):
        cover_path = doc.cover_path
    
    meta = f'Title: Cover\nBook: {book}\nCSS:../Styles/style.css\n\n'
    body = f'<body class="cover">\n\t<p class="cover">\n\t\t<img class="cover" alt="Cover" src="{cover_path}" />\n\t</p>\n</body>\n  '
    
    md = f'{meta}{body}'
    
    return md

@errwrap()
def get_md(book: int):
    '''
    Retrieve the multimarkdown given book's coverpage from MongoDB.

    Args:
        `book` (int):
            The given book.

    Returns:
        `md` (str): 
            The multimarkdown of the given book's coverpage.
    '''
    sg()
    for doc in Coverpage.objects(book=book):
        return doc.md

#> HTML
@errwrap(exit=False)
def generate_html(book: int):
    '''
    Create the HTML for the cover page of the given book.

    Args:
        `book` (int):
            The given book.

    Raises:
        `OSError`
            ose: Unable to convert multimarkdown into HTML

    Returns:
        `html` (str): 
            The HTML for the cover page of the given book.
    '''
    md_path = str(generate_md(book))
    log.debug(f"MD Path: {md_path}")
    html_path = str(generate_html(book))
    log.debug(f"HTML Path: {html_path}")
    mmd_cmd = ['mmd',html_path,md_path]
    log.debug(f"MMD Command: {mmd_cmd}")
    try:
        result = run(mmd_cmd)
        log.debug(f"Successfully converted book {book}'s multimarkdown into html")
    except OSError as ose:
        log.error({"error": ose, "filename": "book.py", "function": f"generate_html(book:{book})"})
        raise ose
    else:
        run(['yay'])
    with open (html_path, 'r') as infile:
        html = infile.read()
        log.debug(f"Read Book {book}'s cover page's html from disk.")
        
    return html

@errwrap()
def get_html(book: int):
    '''
    Retrieve the html of the given book's cover page.

    Args:
        `book` (int):
            The given book.

    Returns:
        `html` (str): 
            The html of the given book's cover page.
    '''
    sg()
    for doc in Coverpage.objects(book=book):
        return doc.html


@errwrap()
def create_coverpage(book: int, test: bool=False):
    sg()
    if test:
        log.info("Connected to MongoDB.")
    filename = generate_filename(book)
    if test:
        log.info(f'Filename: {filename}')
    md_path = generate_md_path(book)
    if test:
        log.info(f'MD Path: {md_path}')
    html_path = generate_html_path(book)
    if test:
        log.info(f'HTML Path: {html_path}')
    md = generate_md(book)
    if test:
        log.info(f'Multimarkdown: {md}')
    html = generate_html(book)
    if test:
        log.info(f'html: {html}')
    
    sg()
    if test:
        log.info("Reconnected to MongoDB.")
    new_coverpage = Coverpage(
        book = book,
        filename = filename,
        md_path = md_path,
        html_path = html_path,
        md = md,
        html = html
    )
    new_coverpage.save()
    log.info(f"Added Book {book}'s coverpage to MongoDB.")
