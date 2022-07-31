# core/scrape.py

from json import dump, dumps, load
from os import system
import re
from pprint import pprint

from markdown2 import markdown
from requests import get
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm.auto import tqdm, trange
from bs4 import BeautifulSoup
import requests

import core.chapter as chapter_
from core.base import BASE
from core.atlas import max_title, sg
from core.log import errwrap, log
from core.yay import finished

#> Constants
CHROME_DRIVER = "driver/chromedriver"
EDGE_DRIVER = "driver/msedgedriver.exe"
TOC_PATH = "json/toc.json"

@errwrap()
def generator_list(chunk_size: int = 4) -> list:
    """
    Generate a list of chapter numbers.
    """
    for j in range(1, 3463, chunk_size):
        if j == 3095 | j == 3117:
            continue
        else: 
            yield j
            
@errwrap()
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(1, 3463, n):
        if i == 3095 | i == 3117:
            continue
        else:
            yield l[i : i + n]

@errwrap()
def parse_chapter_title(title: str) -> str:
    """
    Parse chapter title.
    """
    if ':' in title:
        title = title.replace(":", "")
    if '-' in title:
        title = title.replace("-", "")
    title = title.strip()
    return title

@errwrap()
def generate_toc() -> dict:
    """
    Generate a TOC from the Super Gene website.
    """
    TOC_PATH = 'json/toc.json'
    DRIVER_PATH = 'Driver/chromedriver'
    CHAPTERS_PATH = 'books/chapters'
    TOC_URL = "https://bestlightnovel.com/novel_888112448"
    
    page = requests.get(TOC_URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(id="list_chapter")
    links = results.find_all('a')
    
    chapters = {}
    for link in tqdm(links, unit="ch", desc="Generating Table of Contents"):
        
        #> Parse Chapter Number
        link_contents = link.contents
        log.info(f"Link Contents: {link_contents}")
        title = str(link).strip()
        regex = f'Chapter (\d+)'
        chapter_number_match = re.search(regex, title, re.I)
        chapter_number = int(chapter_number_match.group(1))
        
        #> Parse Chapter Title
        title = parse_chapter_title(title)
        title = title.split(str(chapter_number))[1]
        title = str(title).strip()
        
    
        #> Parse Chapter URL
        link_url = link['href']
        
        #> Parse Section and Chapter
        section = chapter_.generate_section(chapter_number)
        book = chapter_.generate_book(chapter_number)
        filename = chapter_.generate_filename(chapter_number)
        md_path = chapter_.generate_md_path(chapter_number)
        html_path = chapter_.generate_html_path(chapter_number)
        chapter_meta_dict= {
            "chapter": chapter_number,
            "section": section,
            "book": book,
            "title": title,
            "url": link_url,
            "filename": filename,
            "md_path": md_path,
            "html_path": html_path
        }
        log.info(f"Chapter {chapter_number}'s metadata: {chapter_meta_dict}")
    
    try:
        with open (TOC_PATH, 'w') as outfile:
            dump (chapters, outfile, indent=2)
    except Exception as e:
        toc_json = dumps(chapters, indent=2)
        with open (TOC_PATH, 'w') as outfile:
            outfile.write(toc_json)
    
    finished("Generated Table of Contents", "core/scrape.py",)
