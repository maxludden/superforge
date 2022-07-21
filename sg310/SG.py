# SG.py

# Dependencies
from main import max_title, atlas, atlas_lp, lp
from tqdm.auto import tqdm
from json import load, dump
from markdown2 import markdown
from re import findall, search, sub, MULTILINE, IGNORECASE
import re
import logging
import sys


# Declair project paths as constsants
CH_INDEX = "JSON/chapter_index.json"
CHAPTER_JSON = "JSON/chapter.json"
SECTIN_JSON= "JSON/section.json"
LOG_PATH = "logs/sg.log"


# Declaire logger
log = logging.getLogger()
log.setLevel(logging.INFO)
db_file_handler = logging.FileHandler(LOG_PATH, mode="w")
log.addHandler(db_file_handler)
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)

with open (CHAPTER_JSON, 'r') as infile:
    chapters = dict((load(infile)))
    