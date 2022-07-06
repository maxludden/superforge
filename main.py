# SuperForge/main
import os
import re
import sys
from json import dump, dumps, load, loads
from pprint import pprint
from subprocess import run

from bs4 import BeautifulSoup
from icecream import ic
from tqdm.auto import tqdm

import core.book as book_
import core.chapter as chapter_
import core.default as default_
import core.defaultdoc as defaultdoc_
from core.atlas import BASE, sg
from core.endofbook import make_endofbooks
from core.epubmeta import create_all_epubmeta, update_all_epubmeta
from core.log import errwrap, fix_tags, log, new_run
from core.meta import create_meta, write_metadata
from core.section import fix_md, make_sections, save_html
from core.sort_json import export_chapters
from core.titlepage import Titlepage, generate_titlepages, html_check
from yaml import SafeLoader, load_all

#. Start a new run
new_run()

#. Coverpage
#> cb.create_coverpage()
# cb.update_filepaths()
#cb.test(1)

#. Chapters
#> make_chapters()
# verify_chapters()
chapter_.update_html_paths()

#. Titlepages
#> generate_titlepages()
# html_check()

#. EndOfBook
#> make_endofbooks()

#. Section Pages
#> make_sections()
# fix_md()
# save_html()

#. Export Chapters to disk
#> Export Chapters
# export_chapters()

#. Metadata
#> create_meta()
# write_metadata()

#. Epubmeta
#> create_all_epubmeta()
# update_all_epubmeta()

#. Defaultdoc
sg(test=True)
for doc in book_.Book.objects():
    log.info(f"Book: {doc.book}")




fix_tags()
