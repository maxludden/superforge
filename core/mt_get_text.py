# core/mt_get_text.py

from json import load, loads, dump, dumps
from time import perf_counter
import concurrent.futures
from functools import wraps

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from core.log import log
from core.chapter import Chapter, generate_book
from core.base import BASE

# Delcare Custom Exceptions
class SettingsButtonNotFound(NoSuchElementException):
    chapter: int
    msg: str = "Unable to find settings button."
    
    def __init__(self, chapter: int, msg: str = "Unable to find settings button."):
        self.chapter = chapter
        self.msg = msg
        
    def __repr__(self):
        return f"SettingsButtonNotFound: Chapter {self.chapter}: {self.msg}"

class BadWordsButtonNotFound(NoSuchElementException):
    chapter: int
    msg: str = "Unable to find bad words button."
    
    def __init__(self, chapter: int, msg: str = "Unable to find bad words button."):
        self.chapter = chapter
        self.msg = msg
        
    def __repr__(self):
        return f"BadWordsButtonNotFound: Chapter {self.chapter}: {self.msg}"

class ChapterTextNotFound(NoSuchElementException):
    chapter: int
    msg: str = "Unable to find chapter text."
    
    def __init__(self, chapter: int, msg: str = "Unable to find chapter text."):
        self.chapter = chapter
        self.msg = msg
        
    def __repr__(self):
        return f"ChapterTextNotFound: Chapter {self.chapter}: {self.msg}"

class ChapterTextNotFoundInTime(TimeoutException):
    chapter: int
    msg: str = "Unable to find chapter text in allowed time."
    
    def __init__(self, chapter: int, msg: str = "Unable to find chapter text in allowed time."):
        self.chapter = chapter
        self.msg = msg
        
    def __repr__(self):
        return f"ChapterTextNotFoundInTime: Chapter {self.chapter}: {self.msg}"

class UnableToParseChapterText(Exception):
    chapter: int
    msg: str = "Unable to parse chapter text."
    
    def __init__(self, chapter: int, msg: str = "Unable to parse chapter text."):
        self.chapter = chapter
        self.msg = msg
        
    def __repr__(self):
        return f"UnableToParseChapterText: Chapter {self.chapter}: {self.msg}"

# Declare global variables
chapters = []
chapter_urls = []
chapter_texts = []
chapter_dicts = {}
NUM_THREADS = 24

def timer(*, entry: bool = True, exit: bool = True, level="DEBUG"):
    def wrapper(func):
        name = func.__name__
        
        @wraps(func)
        def wrapped(*args, **kwargs):
            timer_log = log.opt(depth=1)
            if entry:
                t1 
                timer_log(level,)

def browser():
    driver = webdriver.Chrome(headless=True)
    return driver

with open('json/toc2.json', 'r') as infile:
    toc = load(infile)

def get_chapter_dict(chapter: int) -> dict:
    chapter_dict = toc[chapter]
    return chapter_dict

def get_chapter_text(chapter: int) -> str:
    chapter_dict = get_chapter_dict(chapter)
    chapter_url = chapter_dict['url']
    chapter = int(chapter_dict["chapter"])
    chapter_title = chapter_dict["title"]
    driver = browser()
    driver.get(chapter_url)
    
    # Wait for Settings Button to load, then click it
    try:
        settings_button = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.LINK_TEXT, "SETTING"))
        )
        settings_button.click()
    except NoSuchElementException:
        raise SettingsButtonNotFound(chapter)
    else:
        log.debug(f"Chapter {chapter}: Clicked settings button.")
    # Click Bad Words Button
    try:
        change_bad_words_button = driver.find_element(
            By.XPATH, '//*[@id="trang_doc"]/div[6]/div[1]/div[2]/ul/li[5]/a'
        )
        change_bad_words_button.click()
    except NoSuchElementException:
        raise BadWordsButtonNotFound(chapter)
    else:
        log.debug(f"Chapter {chapter}: Clicked bad words button.")
        
    # Wait for text to load; then get it
    try:
            text = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "vung_doc"))
            )
            text = driver.find_element(By.ID, "vung_doc")
            paragraphs = text.find_elements(By.TAG_NAME, "p")
            text = ""
            for paragraph in paragraphs:
                text = str(text + paragraph.text + "\n\n")

            # Strip erroneous whitespace characters
            text = text.strip()
            
    except NoSuchElementException:
        raise ChapterTextNotFound(chapter)
    except TimeoutException:
        raise ChapterTextNotFoundInTime(chapter)
    else:
        log.debug(f"Chapter {chapter}: Found chapter text.")
        
    # Parse Text
    try:
        text_split = text.split('\n\n')
        new_text_split = []
        for x, line in enumerate(text_split, start = 1):
            if x == 1:
                if str(chapter) in line:
                    line = ""
                elif chapter_title in line:
                    line = ""
                new_text_split.append(line)
                continue
            if x == 2:
                if "Nyoi-Bo" in line | "nyoi-bo" in line:
                    line = ""
                elif str(chapter) in line:
                    line = ""
                new_text_split.append(line)
                continue
            new_text_split.append(line)
        
        text = "\n\n".join(new_text_split)
        text = text.strip()
    except Exception:
        raise UnableToParseChapterText(chapter)
    else:
        log.debug(f"Chapter {chapter}: Parsed chapter text.")
        
        # Write chapter text to disk
        book = generate_book(chapter)
        chapter_zfill = str(chapter).zfill(4)
        book_zfill = str(book).zfill(2)
        filename = f"chapter-{chapter_zfill}.txt"
        filepath = f"{BASE}/books/book{book_zfill}/text/{filename}"
        
        with open(filepath, "w") as outfile:
            outfile.write(text)
            
        # Write chapter_dict to disk
        chapter_dict = {
            "chapter": chapter,
            "title": chapter_title,
            "url": chapter_url,
            "text": text
        }
        with open (f"json/chapter_dicts/chapter-{chapter_zfill}.json", "w") as outfile:
            dump(chapter_dict, outfile, indent = 4)
        chapter_dicts[chapter] = chapter_dict

    finally:
        driver.quit()
    return text
    
result = timeit.timeit(stmt="get_chapter_text()")