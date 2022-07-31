import logging
import re
import sys
from json import dump, load
from re import I, M, findall, sub

from pymongo import monitoring
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm.auto import tqdm

from core.atlas import sg, BASE
import core.chapter as chapter_
from sg310.SG import badWords, fixDemigod, geno_r, status, removeDotCom
    

LOG_PATH = "logs/supergene.log"
DRIVER_PATH = "driver/chromedriver"


def get_chapter_dict(chapter: str) -> dict:
    with open("json/toc.json", "r") as infile:
        toc = dict((load(infile)))
    chapter_dict = toc[chapter]
    return chapter_dict


def get_chapter(chapter: str) -> None:
    if not chapter:
        chapter = input("Redownload which chapter?")
    text = get_text_from_ch(chapter)
    text = parse_chapter(text, chapter)


def get_text_from_ch(chapter: str) -> str:
    # > Initial Variables
    chapter = str(chapter)
    try:
        chapter_num = int(chapter)
    except:
        log.info(f"Input wasn't valid.")
        get_chapter()
    lines = []
    title_prefix = "Super Gene Chapter "
    title_suffix = " Online | BestLightNovel.com"

    # Get URL
    with open("JSON/toc.json", "r") as infile:
        toc = dict((load(infile)))
    ch_dict = toc[chapter]
    URL = ch_dict["url"]

    # Chrome Webdriver
    PATH = DRIVERS_PATH
    options = ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(PATH, options=options)

    # Get Chapter Page
    driver.get(URL)

    # Get article title
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

            # Save chapter as markdown in chapters/NewChapter.md
            filename = str("chapters/" + chapter + ".md")
            filepath = str("chapters/NewChapter.md")
            with open(filepath, "w", encoding="utf-8") as infile:
                infile.write(text)

            # Update index.saved
            filepath = "JSON/index.json"
            with open(filepath, "r", encoding="utf-8") as infile:
                toc = load(infile)

            toc["re"] = chapter_num
            with open(filepath, "w") as outfile:
                dump(toc, outfile, indent=4, sort_keys=True)
        except:
            print("\n\n\nError 404\nUnable to locate text on page. Quiting Script.\n")
    finally:
        driver.quit()
    return text


def vog(text):
    text = str(text)
    blockquote_regex = [
        r"\n(^\".*?killed.*?beast soul.*?point.*?\")$",
        r"\n(^\".*?flesh.*?point.*?\")$",
        r"\n(^\".*?Xenogeneic.*?hunted.*?gene.*?\")$",
        r"\n(^\".*?hunted.*?:.*?beast soul.*?\")$",
        r"\n(^\".*?killed.*?beast soul.*?inedible.*?\")$",
        r"\n(^\".*?beast soul.*?:.*?\")$",
        r"\n(^\".*?beast soul.*?;.*?\")$",
        r"\n(^\".*?:.*?gene lock.*?\")$",
        r"\n(^\".*?gene.*?\+\d+.*?\")$",
        r"\n(^\".*?hunted.*?found.*?.*?\")$",
        r"\n(^\".*?body.*?evol.*?success.*?\")$",
        r"\n(^\".*?consumed.*?geno point.*?\")$",
        r"\n(^\".*?;.*?status.*?\")$",
        r"\n(^\".*?retrieve.*?beast soul.*?from.*?\")$",
        r"\n(^\".*?obtained.*?random.*?\")$",
        r"\n(^\".*?absorb.*?geno point.*?\")$",
        r"\n(^\".*?announce.*?:.*?\")$",
        r"\n(^\".*?eaten\..*?geno point.*?\")$",
        r"\n(^\".*?egg broken.*?identi.*?\")$",
        r"\n(^\".*?Identifying.*?beast soul.*?\")$",
        r"\n(^\".*?beast soul.*?identi.*?gained.*?\")$",
        r"\n(^\".*?killed.*?beast soul.*?life essence.*?\")$",
        r"\n(^\".*?evolution.*?super body.*?\")$",
        r"^(\".*?killed.*?beast soul.*?geno core.*?flesh.*?\")$",
        r"\n(^\"Deified Gene.*?+1.*?\")$",
        r"\n(^\"God.*?Evolu.*?\")$",
    ]
    matches = []
    for regex in blockquote_regex:
        matches = findall(regex, text, re.I | re.M)
        if matches:
            for match in matches:
                block = str("> " + match)
                block = block.title()
                text = sub(match, block, text, re.I, re.M)
            duplicate_regex = r"^(> > )\""
            duplicate_results = findall(duplicate_regex, text, re.I | re.M)
            if duplicate_results:
                for x in duplicate_results:
                    rep_str = r"> "
                    text = sub(x, rep_str, text, re.I | re.M)
    return text


def parse_chapter(text: str, chapter: str) -> str:
    text = str(text)
    chapter = str(chapter)
    chapter_num = int(chapter)
    chapter_dict = get_chapter_dict(chapter)
    title = chapter_dict["title"]
    tags = {"redownload", "reparsed"}

    # Search for HTML Header in Text:
    remove_meta_regex = r"(Chapter.*\n\n.*?Nyoi-Bo Studio.*\n)\n$|(.*?Nyoi-Bo Studio.*\n)$\n|(.*?Chapter.*$\n)\n"
    article_header = re.search(remove_meta_regex, text, re.I | re.M)
    if article_header:
        # If HTML Header found, replace it with Head
        article_header = article_header.group()
        article_header = str(article_header)
        text = str(text.replace(article_header, ""))
    studioRegex = r"(.*?Nyoi.*\n\n)"
    studioResults = findall(studioRegex, text, re.M | re.I)
    if studioResults:
        text = sub(studioRegex, "", text, flags=re.M | re.I)
    if chapter in text:
        regex_string = str(r"^(.*?)" + chapter + r"(.*)$")
        text = sub(regex_string, "", text)

    # Remove Title and Chapter data from top of chapter
    split_text = text.split("\n\n")
    first2lines = split_text[0:1]
    if title in first2lines:
        for x, line in enumerate(first2lines):
            if title in line:
                line = sub(title, "", text)
                split_text[x] = line
    if chapter in first2lines:
        for x, line in enumerate(first2lines):
            if chapter in line:
                line = sub(chapter, "", text)
                split_text[x] = line
    updated_text = "\n\n".join(split_text)
    if updated_text != text:
        text = updated_text

    # Blockquote - VoG  -----------------------------------------
    vog_text = str(vog(text))
    if vog_text != text:
        if text != "None":
            text = str(vog_text)
            tags.add("vog")
        else:
            sys.exit()

    # Check for Status Table ------------------------------------
    status_text = str(status(text))
    if status_text != text:
        if status_text != "None":
            text = str(status_text)
            tags.add("status")

    # Check for Geno-r Table --------------------------------------
    genoR_text = str(geno_r(text))
    if genoR_text != text:
        if genoR_text != "None":
            text = str(genoR_text)
            tags.add("geno_r")

    # Check for new Beast Soul
    regex = r"(.*?)beast soul(.*?)type(.*?)$"
    chapter_matches = findall(regex, text)
    if chapter_matches:
        tags.add("beast")
    else:
        regex = r"(.*?)type(.*?)beast soul(.*?)$"
        chapter_matches = findall(regex, text)
        if chapter_matches:
            tags.add("beast")

    # Fix censored bad words
    text = badWords(text, chapter)
    parsed_text = str(text)

    # Fix Demigod and Advertisements
    text = fixDemigod(parsed_text)
    text = removeDotCom(text)

    # Fix Jadeskin
    jadeskin_results = findall("jadeskin", text)
    if jadeskin_results:
        for result in jadeskin_results:
            text = sub(result, "Jadeskin", text)
    
    book = chapter_.generate_book(chapter_num)
    book_str = str(book).zfill(2)
    with open(f"books/book{book_str}/ParseChapter.md", "w") as outfile:
        outfile.write(text)

    lp("Parsed Chapter " + chapter + " to chapter/Parsed Chapter.")

    return text  # End of parse_chapter


def remake_doc(text: str, chapter: str) -> None:
    pass


get_chapter(1027)
