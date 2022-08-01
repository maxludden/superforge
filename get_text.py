# utilities/get_text.py

import sys
import multiprocessing as mp
from json import load, dump, loads, dumps
from functools import partial
from itertools import chain

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from dotenv import load_dotenv
from alive_progress import alive_it
import sh

try:
    from core.chapter import Chapter, generate_book
    from core.atlas import sg, get_atlas_uri
    from core.base import BASE
    from core.log import log, errwrap
    from core.download_chapter import get_text_from_ch
except ImportError:
    from chapter import Chapter, generate_book
    from atlas import sg, get_atlas_uri
    from base import BASE
    from log import log
    from core.download_chapter import get_text_from_ch

with open ('json/toc2.json', 'r') as infile:
    toc = load(infile)

def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]
        
def get_text(chapter: int) -> dict:
    chapter = int(toc[str(chapter)]["chapter"])
    CHAPTER = str(chapter)
    with open ("json/toc2.json", 'r') as infile:
        toc = load(infile)
    url = toc[CHAPTER]["url"]
    title = toc[CHAPTER]["title"]
    
    
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
    driver.get(url)

    #> Get Article
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
                    elif title.lower in line.lower:
                        line = ""
                    new_text_split.append(line)
                    continue
                elif x == 2:
                    if "Nyoi-Bo" in line:
                        line = ""
                    elif "nyoi-bo" in line:
                        line = ""
                    elif CHAPTER in line:
                        line = ""
                    new_text_split.append(line)
                    continue
                else:
                    new_text_split.append(line)
            
            text = "\n\n".join(new_text_split)
            text = text.strip()
                        
            # Save chapter as text
            chapter_zfill = str(chapter).zfill(4)
            book = generate_book(chapter)
            book_zfill = str(book).zfill(2)
            filename = f"chapter-{chapter_zfill}.txt"
            filepath = f"{BASE}/books/book{book_zfill}/text/{filename}"
            with open(filepath, "w") as outfile:
                outfile.write(text)
            log.debug(f"Saved chapter {chapter} as {filename}")

            return {"chapter": chapter, "text": text}

        except:
            if text:
                return {"chapter": chapter, "text": text}
            else:
                raise Exception(f"Chapter {chapter}: failed to get text.")
    finally:
        driver.quit()

pool = mp.Pool(mp.cpu_count()-1)

chapters = []
for x in range(1,3463):
    if x == 3095 | x == 3117:
        continue
    else:
        chapters.append(x)

result = pool.map(get_text, chapters)
pool.close()

final_result = list(chain.from_iterable([r.items() for r in result]))
for x in alive_it(final_result,title="Updating MongoDB"):
    sg()
    chapter = int( x["chapter"] )
    for doc in Chapter.objects(chapter=chapter):
        doc.unparsed_text = x["text"]
        doc.save()
        log.debug(f"Updated chapter {doc.chapter}")
        
sh("figlet 'Done!' | lolcat -a")
ffrom