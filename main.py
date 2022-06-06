# SuperForge/main
import os
import re
import sys
from json import dump, load
from subprocess import run

from dotenv import load_dotenv
from tqdm.auto import tqdm

from core.atlas import sg
from core.titlepage import Titlepage, make_titlepages
from core.log import log, new_run, fix_tags
from core.endofbook import make_endofbooks

#. Start a new run
new_run()

#. Titlepages
# make_titlepages()

#. EndOfBook
#make_endofbooks()

#. Section Pages

fix_tags()