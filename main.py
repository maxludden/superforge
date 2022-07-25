# SuperForge/main
import os
import re

# import re
# import sys
from json import dump, dumps, load, loads
from pprint import pprint
from subprocess import run
from multiprocessing import Process, Manager, Pool

from tqdm.auto import tqdm
from dotenv import load_dotenv
from mongoengine import connect

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
import core.titlepage as titlepg
from core.yay import yay, finished

load_dotenv()  # > Load .env file

# . Start a new run
new_run()


sg()  # > Connect to Mongo Database
for doc in tqdm(
    chapter_.Chapter.objects().order_by("chapter"), unit="ch", desc="Editing Chapters"
):

    log.info(doc.__repr__())

msg = "Testing Finished Function and Subsequent Notification"
file = "SUPERFORGE/main.py"
finished(msg, file)

# Fix_log.md tags
fix_tags()
