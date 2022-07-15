# SuperForge/main
import os

# import re
# import sys
from json import dump, dumps, load, loads
from pprint import pprint
from subprocess import run

from tqdm.auto import tqdm

from core.log import errwrap, log, new_run
from core.fix_tags import fix_tags
from core.atlas import sg, BASE
import core.book as book_
import core.chapter as chapter_
import core.cover as cover_
import core.defaultdoc as default_
import core.endofbook as eob_
import core.epubmetadata as epubmd
import core.metadata as coremd
import core.section as section_
import core.old_title as titlepg

# . Start a new run
new_run()



# < Fix tags.
fix_tags()

@errwrap()
def book_to_disk(book: int):
    '''
    Generate or retrive all of the needed documents of the given doc, and write them to disk.

    Args:
        `book` (int):
            The given book.
    '''
