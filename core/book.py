# #core/book.py
from json import dump, dumps, load, loads
from pprint import pprint
from subprocess import run

from bs4 import BeautifulSoup
from markupsafe import Markup, escape
from mongoengine import Document
from mongoengine.fields import IntField, ListField, StringField, UUIDField
from tqdm.auto import tqdm

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
    book = IntField()
    filename = StringField()
    filepath = StringField()
    html = StringField()
    meta = {
        'collection': 'coverpage'
    }

def create_coverpage():
    cover_path = f'{BASE}/json/covers.json'
    with open (cover_path, 'r') as infile:
        covers = dict((load(infile)))
        
    #> Retrieve coverpage dict bay book
    keys = covers.keys()
    new_covers = {}
    for key in keys:
        log.info(f'key: {key}')
        
        html = covers[str(key)]
        
        # bs4.BeautifulSoup
        soup = BeautifulSoup(html, features="html.parser")
        pretty_soup = soup.prettify() # prettify html
        log.info(f'pretty_soup: {pretty_soup}')
        serialized_soup = dumps(soup) # Serialize for JSON storage
        log.info(f'serialized_soup: {serialized_soup}')
        
        filename = f"cover{book}.html"
        book_dir = str(book).zfill(2)
        filepath = f"{BASE}/books/book{book_dir}/html/{filename}"
        
        sg()
        new_cover = Coverpage (
            book = int(key),
            filename = filename,
            filepath = filepath,
            html = serialized_soup
        )
        log.info(f'"New Cover": {new_cover}')
        new_cover.save()
        
