# superforge/core/default.py
#> Imports
import sys

from icecream import ic
from mongoengine import Document
from mongoengine.fields import IntField, ListField, StringField

try:
    import core.book as book_
    import core.chapter as chapter_
    import core.endofbook as eob_
    import core.myaml as myaml
    import core.section as section_
    import core.titlepage as titlepage_
    from core.atlas import BASE, sg
    from core.book import Book
    from core.log import errwrap, log
except ImportError:
    import book as book_
    import chapter as chapter_
    import endofbook as eob_
    import myaml
    import section as section_
    import titlepage as titlepage_
    from atlas import BASE, sg
    from book import Book
    from log import errwrap, log

    #> End of Imports

@errwrap()
def generate_output_file(book: int, test: bool=False):
    '''
    Generate the output-file for the given book.

    Args:
        `book` (int):
            The given book.
        `test` (book)
            Whether this run was used to test.

    Returns:
        `output_file` (str): 
            The output-file for the given book.
    '''
    sg()
    if test:
        log.info("Connected to MongoDB.")
    for doc in book_.Book.objects(book=book):
        if test:
            log.info(f"doc output: {doc.output}")
        return doc.output

sg()
for doc in Book.objects(book=1):
    output = doc.output
    print(f"output: {output}")
