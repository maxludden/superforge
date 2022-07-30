import logging
import re
from json import dump, load

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from checkForUpdates import INDEX_PATH
from main import lp
from core.chapter import generate_section, generate_book

# Full paths
INDEX_PATH = 'json/index.json'
TOC_PATH = 'json/toc.json'
driverMacPath = 'Drivers/chromedriver'
CHAPTERS_PATH = 'books/chapters'
LOG_FILE = 'logs/checkForUpdates.log'

load_dotenv()

print('New Run')

toc = {}
count = 0

# Use bs4 to get bad words off chapter text
URL = "https://bestlightnovel.com/novel_888112448"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")
results = soup.find(id="list_chapter")
links = results.find_all("a")

# For every link in "list_chapter"
for link in links:
    link_text = str(link.text)
    link_text = link_text.strip()
    chapter = int(re.findall(r'\d+', link_text)[0])
    chapter_str = str(chapter)
    section = generate_section(chapter)
    book = generate_book(chapter)
    

    # Parse chapter title
    title = link_text.split(chapter)[1]
    if ':' in title:
        title = title.replace(':', '')
    if '-' in title:
        title = title.replace('-', '')
    title = title.strip()
    if title == '':
        try:
            title = link_text.split(chapter)[2]
            if ':' in title:
                title = title.replace(':', '')
            if '-' in title:
                title = title.replace('-', '')
            title = title.strip()
        except:
            title = link_text  # End of Title

    # Chapter URL
    link_url = link["href"]

    # Save Path
    chapter_dir_str = str(chapter).zfill(4)
    book_str = str(book)
    book_dir_str = book_str.zfill(2)
    savePath = str(f"{CHAPTERS_PATH}'/chapter-'{chapter_str}.txt")

    # Fix Chapter 39.1
    if "Saint Paul (1)" in title:
        toc[39] = {"title": "Saint Paul - Part 1",
                    "url": link_url, "path": savePath}
    elif "Saint Paul (2)" in title:
        toc[40] = {"title": "Saint Paul - Part 2",
                    "url": link_url, "path": savePath}
    else:
        toc[chapter_str] = {
            "title": title,
            "url": link_url, 
            "path": savePath}

    print("Saved Chapter " + chapter + " to TOC")
    # Update Count
    if chapter_number > count:
        count = chapter_number

print("count =" + str(count))

# Update Index Count ------------------------------------------------------------
logging.debug('Updating Index')

with open(INDEX_PATH, 'r')as infile:
    index = load(infile)
index['count'] = count
with open(INDEX_PATH, 'w') as outfile:
    dump(index, outfile, indent=4, sort_keys=True)
    lp('Saved updated index')  # Finish updated Index Count

# Write Table of Contents
with open(TOC_PATH, 'w') as outfile:
    dump(toc, outfile, indent=4, sort_keys=True)
    logging.debug('Updated Table of Contents.\n\tFilepath: ' +
                TOC_PATH + '\n\tLatest Chapter: ' + str(count))
# End of getToc()


