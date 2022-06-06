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

#>Titlepages
make_titlepages()

fix_tags()