# SuperForge/main
import os
import re
from pprint import pprint

# import re
# import sys
from json import dump, dumps, load, loads
from pprint import pprint
from subprocess import run
from multiprocessing import Process, Manager, Pool, cpu_count

from tqdm.asyncio import tqdm
from dotenv import load_dotenv
from mongoengine import connect
from alive_progress import alive_bar, alive_it

from core.log import errwrap, log, new_run
from core.fix_tags import fix_tags
from core.atlas import sg, max_title
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
import core.get_toc as toc_
from core.yay import yay, finished
import core.download_chapter as dc
from core.base import BASE

load_dotenv()  # > Load .env file

# . Start a new run
new_run()

sg()
chapters = []
for doc in Chapter.objects():
    if doc.chapter > 2473:
        chapters.append(doc.chapter)


def browser():  
    driver = webdriver.Chrome()
    return driver
 
def get_text(link):
    driver = browser()  # Each browser use different driver.
    driver.get(link)

def multip():

    pool = Pool(processes=7)
    for i in range(0, len(chapters)):
        pool.apply_async(dc.get_text_from_ch, args={chapters[i]})

    pool.close()
    pool.join()
    
# if __name__ == '__main__':
#     multip()

print (cpu_count)

# Fix_log.md tags
fix_tags()
