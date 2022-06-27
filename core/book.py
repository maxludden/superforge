# #core/book.py
from json import dump

from mongoengine import Document
from mongoengine.fields import IntField, ListField, StringField, UUIDField
from tqdm.auto import tqdm

try:
    from core.atlas import BASE, max_title, sg
    from core.log import errwrap, log
except ImportError:
    from atlas import BASE, max_title, sg
    from log import errwrap, log

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
    book = IntField()
    filename = StringField()
    filepath = StringField()
    html = StringField()
    meta = {
        'collection': 'coverpage'
    }

def create_coverpage():
    #> Loop threw books and read coverpage
    coverpages = {}
    books = range(1, 11)
    for book in books:
        book = int(book)
        book_dir = str(book).zfill(2)
        filename = f'cover{book}.html'
        filepath = f'{BASE}/books/book{book_dir}/html/{filename}'
        
        html = f'''<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
    <meta charset="utf-8"/>
    <meta name="book" content="{book}"/>
    <link type="text/css" rel="stylesheet" href="../Styles/style.css"/>
    <meta name="viewport" content="width=device-width"/>
    <title>Cover {book}</title>
</head>

<body class="cover">
    <p class="cover">
        <img class="cover" alt="Cover Page" src="../Images/cover{book}.png" />
    </p>
</body>
'''
        coverpages[book]= {
            "book": book,
            "filename": filename,
            "filepath": filepath,
            "html": html
        }
    with open ("json/coverpages.json", 'w') as outfile:
        dump(coverpages, outfile, indent=4)

@errwrap()
def generate_filename(book: int):
    return f"cover{book}.html"

@errwrap()
def get_filename(book: int):
    sg()
    for doc in Coverpage.objects(book=book):
        return doc.filename
    
@errwrap()
def generate_filepath(book: int):
    filename = get_filename (book)
    book_dir = str(book).zfill(2)
    filepath = f'{BASE}/books/book{book_dir}/html/{filename}'
    return filepath

def save_filepath(book: int):
    filepath = generate_filepath(book)
    sg()
    for doc in Coverpage.objects(book=book):
        doc.filepath = filepath
        doc.save()
        log.info(f"Saved Book {book}'s filepath to MongoDB.")

def get_filepath(book: int):
    sg()
    for doc in Coverpage.objects(book=book):
        return doc.filepath


@errwrap()
def update_filepath(book: int):
    sg()
    for doc in Coverpage.objects(book=book):
        doc.filepath = generate_filepath(doc.book)
        doc.save()
        


@errwrap()
def test(book: int):
    '''
    Tests the connection to the MongoDB Collection: Coverpage for the given book.

    Args:
        `book` (int):
            The Given book
    '''
    sg()
    for doc in Coverpage.objects(book=book):
        print (f"MongoDB Coverpage Filepath: {doc.filepath}")
