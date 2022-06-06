# #core/book.py

from mongoengine import Document
from mongoengine.fields import IntField, StringField, ListField, UUIDField


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


# > Declairing Static Variables
written: str = "Written by Twelve Winged Burning Seraphim"
edited: str = "Complied and Edited by Max Ludden\n\n"
TEXT = f"{written}\n{edited}"