#> superforge/core/defaultdoc.py

#> Dependancies
import os
from platform import platform

from dotenv import load_dotenv
from mongoengine import Document, connect, disconnect_all
from mongoengine.fields import IntField, ListField, StringField
from tqdm.auto import tqdm

def import_core(test: bool=False):
    modules = [
        'Book',
        'Chapter',
        'End of Book',
        'MyYaml',
        'Section',
        'Title Page',
    ]
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
        if test:
            log.info(f"Loaded modules from core:\n\t")
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