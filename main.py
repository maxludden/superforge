# SuperForge/main
import os
import re
from pprint import pprint
from functools import reduce

# import re
# import sys
from json import dump, dumps, load, loads
from pprint import pprint
from subprocess import run
from multiprocessing import Process, Manager, Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor, as_completed

# from tqdm.asyncio import tqdm
from dotenv import load_dotenv
# from mongoengine import connect
from alive_progress import alive_bar, alive_it

from core.log import errwrap, log, new_run
from core.fix_tags import fix_tags
from core.atlas import sg, BASE, max_title
# import core.book as book_
# import core.chapter as chapter_
# from core.chapter import Chapter, generate_section, generate_book
# import core.cover as cover_
# import core.defaultdoc as default_
# import core.endofbook as eob_
# import core.epubmetadata as epubmd
# import core.metadata as coremd
# import core.section as section_
# import core.titlepage as titlepg
# import core.get_toc as toc_
# from core.yay import yay, finished
# import core.download_chapter as dc
from core.mt_get_text import chapter_gen, get_chapter_text

load_dotenv()  # > Load .env file

# . Start a new run
new_run()

# read toc2
with open("json/toc2.json", "r") as infile:
    toc = load(infile)

unparsed_text = {}

with alive_bar(3460,title = "Downloading chapters", dual_line=True) as bar:
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [ executor.submit(get_chapter_text, chapter_gen())]
        results = []
        for result in as_completed(futures):
            results.append(result)
            bar()
    


# Fix_log.md tags
fix_tags()