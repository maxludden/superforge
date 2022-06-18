# SuperForge/main
import os
import re
import sys
from json import dump, load
from pprint import pprint
from subprocess import run

from tqdm.auto import tqdm

from core.atlas import errwrap, sg
from core.book import create_coverpage
from core.chapter import make_chapters, verify_chapters, write_book_md
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
create_coverpage(1, test=True)

#. Chapters
#> make_chapters()
# verify_chapters()

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


fix_tags()
