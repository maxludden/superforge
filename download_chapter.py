# core/download_chapter.py

import re
import sys
from json import dump, load
from re import I, M, findall, sub
from time import sleep
from typing import KeysView

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm.auto import tqdm
from alive_progress import alive_it, alive_bar
import sh

from core.atlas import sg, BASE, max_title
from core.log import log, errwrap
from core.chapter import Chapter
import core.chapter as chapter_

DRIVER_PATH = "/home/maxludden/dev/py/superforge/driver/chromedriver"

def get_text_from_ch(chapter: int) -> str:
    # > Get chapter document from MOngoDB
    sg()
    chapter_dict = Chapter.objects(chapter=chapter).first()
    TITLE = chapter_dict.title
    CHAPTER = str(chapter_dict.chapter)
    URL = chapter_dict.url
    
    # > Initial Variables
    lines = []
    title_prefix = "Super Gene Chapter "
    title_suffix = " Online | BestLightNovel.com"

    #> Chrome Webdriver
    PATH = DRIVER_PATH
    options = ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(PATH, options=options)

    #> Get Chapter Page
    driver.get(URL)

    #> Get article title
    article_title = driver.title
    article_title = str(article_title)
    article_title = article_title.replace(title_prefix, "").replace(title_suffix, "")

    try:
        settings_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "SETTING"))
        )
        settings_button.click()

        change_bad_words_button = driver.find_element(
            By.XPATH, '//*[@id="trang_doc"]/div[6]/div[1]/div[2]/ul/li[5]/a'
        )
        change_bad_words_button.click()
        try:
            text = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "vung_doc"))
            )
            text = driver.find_element(By.ID, "vung_doc")
            paragraphs = text.find_elements(By.TAG_NAME, "p")
            text = ""
            for paragraph in paragraphs:
                text = str(text + paragraph.text + "\n\n")

            # Strip erronious whitespace characters
            text = text.strip()
            
            text_split = text.split('\n\n')
            new_text_split = []
            for x, line in enumerate(text_split, start = 1):
                if x == 1:
                    if CHAPTER in line:
                        line = ""
                    elif TITLE in line:
                        line = ""
                    new_text_split.append(line)
                    continue
                if x == 2:
                    if "Nyoi-Bo" in line:
                        line = ""
                    elif "nyoi-bo" in line:
                        line = ""
                    elif CHAPTER in line:
                        line = ""
                    new_text_split.append(line)
                    continue
                new_text_split.append(line)
            
            text = "\n\n".join(new_text_split)
            text = text.strip()
                        
            # Save chapter as text
            chapter_zfill = str(chapter).zfill(4)
            
            book = generate_book(chapter)
            book_zfill = str(chapter_dict.book).zfill(2)
            filename = f"chapter-{chapter_zfill}.txt"
            filepath = f"{BASE}/books/book{book_zfill}/text/{filename}"
            with open(filepath, "w") as outfile:
                outfile.write(text)
            log.debug(f"Saved chapter {chapter} as {filename}")
            
            #> save chapter to MongoDB
            sg("LOCALDB")
            doc = Chapter.objects(chapter=chapter).first()
            doc.chapter_dict.unparsed_text = text
            doc.save()
            
            return text

        except:
            log.warning(f"Error 404\nChapter {chapter}: Unable to locate text on page.\n")
    finally:
        driver.quit()
    return text

with open ("json/toc2.json", 'r') as infile:
    toc = load(infile)

keys = toc.keys()
for key in alive_it(keys):
    chapter = toc[key]["chapter"]
    text = get_text_from_ch(chapter)