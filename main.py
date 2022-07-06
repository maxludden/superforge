# SuperForge/main
import os
# import re
# import sys
from json import dump, dumps, load, loads
from pprint import pprint
from subprocess import run

from tqdm.auto import tqdm

from core.log import errwrap, log
from core.atlas import sg, BASE
import core.book as book_
import core.chapter as chapter_
import core.cover as cover_
import core.defaultdoc as default_
import core.endofbook as eob_
import core.epubmetadata as epubmd
import core.metadata as coremd
import core.section as section_
import core.titlepage as titlepg

#. Start a new run
core_log.new_run()

#. Coverpage


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
