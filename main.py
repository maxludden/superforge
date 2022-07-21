# SuperForge/main
import os
import re

# import re
# import sys
from json import dump, dumps, load, loads
from pprint import pprint
from subprocess import run

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

load_dotenv()
# . Start a new run
new_run()

URI = os.environ.get("SUPERGENE")
connect("supergene", host=URI)

with open ("json/chapter.json", 'r') as infile:
    chapters = dict((load(infile)))
    
# for doc in tqdm(chapter_.Chapter.objects(), unit="ch",desc="Chapter"):
#     regex = re.compile(r"^((?P<class>\w+) Geno Core: (?P<core>.*))$\n")
#     matches = re.findall(regex, doc.text, re.M |re.I)
#     if len(matches) < 0:
#         for match in matches:
#             complete = match.group[0]
#             class_group = match.group["class"]
#             core_group = match.group["core"]
#             log.info(f"Match: {complete}\nClass: {class_group}\nCore: {core_group}")

# < Fix tags.
fix_tags()
