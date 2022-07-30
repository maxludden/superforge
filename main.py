# SuperForge/main
import os
import re
from pprint import pprint

# import re
# import sys
from json import dump, dumps, load, loads
from pprint import pprint
from subprocess import run
from multiprocessing import Process, Manager, Pool

from tqdm import tqdm
from dotenv import load_dotenv
from mongoengine import connect

from core.log import errwrap, log, new_run
from core.fix_tags import fix_tags
from core.atlas import sg, BASE, max_title
import core.book as book_
import core.chapter as chapter_
from core.chapter import Chapter, generate_section, generate_book
import core.cover as cover_
import core.defaultdoc as default_
import core.endofbook as eob_
import core.epubmetadata as epubmd
import core.metadata as coremd
import core.section as section_
import core.titlepage as titlepg
import get_toc as toc_
from core.yay import yay, finished

load_dotenv()  # > Load .env file

# . Start a new run
new_run()

toc_.get_toc()

# Fix_log.md tags
fix_tags()
