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
from utilities.yay import yay

load_dotenv()
# . Start a new run
new_run()

# URI = os.environ.get("SUPERGENE")
# connect("supergene", host=URI)
chapter = 1027
sg()
doc = chapter_.Chapter.objects(chapter=chapter).first()
doc.md =chapter_.generate_md(chapter, save=True, write=True)
doc.html =chapter_.generate_html(chapter, save=True)
doc.save()
yay()


# < Fix tags.
fix_tags()
