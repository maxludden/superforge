# superforge/core/default.py
#> Imports
import sys

from icecream import ic
from mongoengine import Document
from mongoengine.fields import IntField, ListField, StringField


import core.book as book_
import core.chapter as chapter_
import core.endofbook as eob_
import core.myaml as myaml
import core.section as section_
import core.titlepage as titlepage_
from core.atlas import BASE, sg
from core.log import errwrap, log

    #> End of Imports

@errwrap()
def generate_output_file(book: int):
    '''
    Generate the output-file for the given book.

    Args:
        `book` (int):
            The given book.

    Returns:
        `output_file` (str): 
            The output-file for the given book.
    '''
    sg()
    for doc in book_.Book.objects(book=book):
        return doc.output

ic(generate_output_file(1))
