# core/mt_get_text.py

from json import load, loads, dump, dumps
from time import perf_counter_ns
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

#> Declare Custom Exceptions
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

    def __init__(
        self, chapter: int, msg: str = "Unable to find chapter text in allowed time."
    ):
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

#> Setup


NUM_THREADS = 24
chapter_dicts = []

# read toc2
def read_toc():
    with open("json/toc2.json", "r") as infile:
        toc = dict((load(infile)))
    return toc

# Function Timer Decorator
def timer(*, entry: bool = True, exit: bool = True, level="DEBUG"):
    """
    A decorator that logs the entry of a function call, its exit, calculates the duration of the function and logs it.

    Args:
        `entry` (bool, optional): _description_. Defaults to True.
        `exit` (bool, optional): _description_. Defaults to True.
        `level` (str, optional): _description_. Defaults to "DEBUG".
    """

    def wrapper(func):
        name = func.__name__
        t1 = 0
        t2 = 0

        @wraps(func)
        def wrapped(*args, **kwargs):
            timer_log = log.opt(depth=1)
            t1 = perf_counter()
            if entry:
                timer_log.log (level,f"Entered {name}() at {t1})\n<code>args: {args}\nkwargs: {kwargs}</code>",
                )
            result = func(*args, **kwargs)
            t2 = perf_counter()
            if exit:
                timer_log.log(level, f"Exiting {name}() @ {t2}<code>\nresult:\n<{result}</code>"
                )
            return result

        duration = t2 - t1
        log.debug(f"Function {name}() took {duration} seconds.")
        return wrapped

    return wrapper


#> Driver
# called by get_chapter_text()
def browser():
    chromeoptions = webdriver.ChromeOptions().add_argument("--headless")
    driver = webdriver.Chrome(options=chromeoptions)
    return driver

# called by get_chapter_text()

def get_chapter_dict(chapter: int) -> dict:
    toc = read_toc()
    chapter_dict = toc[str(chapter)]
    return chapter_dict


 # called by get_chapter_text()
def click_settings(driver, chapter: int):
    # Wait for Settings Button to load, then click it
    try:
        settings_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "SETTING"))
        )
        settings_button.click()
    except NoSuchElementException:
        raise SettingsButtonNotFound(chapter)
    else:
        log.debug(f"Chapter {chapter}: Clicked settings button.")


# @timer() # called by get_chapter_text()
def click_bad_words(driver, chapter: int):
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


# @timer()# called by get_chapter_text()
def scrape_chapter_text(driver, chapter: int) -> str:
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
    return text


# @timer() # called by get_chapter_text()
def parse_chapter_text(chapter: int, text: str) -> str:
    # Get Chapter_Dict
    chapter_dict = get_chapter_dict(chapter)
    title = chapter_dict["title"]

    # Parse Text
    try:
        text_split = text.split("\n\n")
        new_text_split = []
        for x, line in enumerate(text_split, start=1):
            if x == 1:
                if str(chapter) in line:
                    line = ""
                elif title.lower() in line.lower():
                    line = ""
                new_text_split.append(line)
                continue
            if x == 2:
                if "Nyoi-Bo" in line:
                    line = ""
                elif "nyoi-bo" in line:
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
    return text

count = 0
timer = {}
# @timer() 
def get_chapter_text(chapter: int) -> str:
    t1 = perf_counter_ns()
    CHAPTER = str(chapter)
    with open ("json/toc2.json", "r") as infile:
        toc = load(infile)
        chapter_url = toc[CHAPTER]["url"]
        chapter = int(toc[CHAPTER]["chapter"])
        chapter_title = toc[CHAPTER]["title"]
    driver = browser()
    driver.get(chapter_url)

    click_settings(driver, chapter)
    click_bad_words(driver, chapter)
    text = scrape_chapter_text(driver, chapter)
    text = parse_chapter_text(chapter, text)

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
        "text": text,
    }
    with open(f"json/chapter_dicts/chapter-{chapter_zfill}.json", "w") as outfile:
        dump(chapter_dict, outfile, indent=4)
    chapter_dicts.append(chapter_dict)

    driver.quit()
    
    t2 = perf_counter_ns()
    elapsed_time = t2 - t1
    timer = f"Chapter {chapter}: elapsed time: {elapsed_time}\n"
    with open ('json/timer.text', 'a') as outfile:
        outfile.write(timer)
        
    return chapter_dict


# with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
#    futures = executor.map(get_chapter_text, chapter_gen())
