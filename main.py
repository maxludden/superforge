# SuperForge/main
import os
import re
import sys
from json import dump, load
from subprocess import run

from tqdm import tqdm

from core.atlas import sg
from core.chapter import make_chapters, verify_chapters, write_book_md
from core.endofbook import make_endofbooks
from core.log import fix_tags, log, new_run
from core.section import make_sections
from core.sort_json import export_chapters
from core.titlepage import Titlepage, make_titlepages

#. Start a new run
new_run()

#. Chapters
# make_chapters()
# verify_chapters()
for book in range(4,11):
    write_book_md(book)

#. Titlepages
# make_titlepages()

#. EndOfBook
# make_endofbooks()

#. Section Pages
# make_sections()

#> Export Chapters
##export_chapters()

fix_tags()
