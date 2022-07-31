# SG3.10/checkForUpdates.py
import datetime
import logging
import re
import sys
from json import dump, dumps, load, loads

import requests
from bs4 import BeautifulSoup
from mongoengine import Document, connect
from mongoengine.fields import (DateTimeField, IntField, ListField,
                                StringField, URLField)
# Supergene mongoDB
from pymongo import monitoring
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm.auto import tqdm

from main import Chapter, Section, atlas, get_toc, log, lp, max_title
from SG import db_parse_chapter

# Full paths
INDEX_PATH= 'JSON/index.json'
TOC_PATH = 'JSON/toc.json'
DRIVERS_PATH = "Driver/chromedriver"
CHAPTERS_DIR = '/Users/maxludden/Dev/sg38/chapters'
JSON_DIR = '/Users/maxludden/Dev/sg38/json'
NEEDS_REV_DIR = '/Users/maxludden/Dev/sg38/needsRev'
MD_DIR = '/Users/maxludden/Dev/sg38/MD'
DRIVERS_DIR = '/Users/maxludden/Dev/sg38/drivers'
LOGS_DIR = '/Users/maxludden/Dev/sg38/logs'
LOG_PATH = '/Users/maxludden/Dev/sg38/Logs/checkForUpdates.log'

log = logging.getLogger()
log.setLevel(logging.INFO)
logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                    format='%(asctime)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')


class CommandLogger(monitoring.CommandListener):
    def started(self, event):
        log.debug("Command {0.command_name} with request id "
                  "{0.request_id} started on server "
                  "{0.connection_id}".format(event))

    def succeeded(self, event):
        log.debug("Command {0.command_name} with request id "
                  "{0.request_id} on server {0.connection_id} "
                  "succeeded in {0.duration_micros} "
                  "microseconds".format(event))

    def failed(self, event):
        log.debug("Command {0.command_name} with request id "
                  "{0.request_id} on server {0.connection_id} "
                  "failed in {0.duration_micros} "
                  "microseconds".format(event))

monitoring.register(CommandLogger())

# User defined functions -------------------------
def correct_title(chapter,title):
    chapter = str(chapter)
    chapterNum = int(chapter)
    cases = [9,17,26,47,52,53,60,67,68,70,74,83,95,246,305,485]
    if chapterNum in cases:
        switcher = {
            9: "Sacred-Blood Creature",
            17: "Unexpected Encounter",
            26: "Mutant Three-Eyed Cat",
            47: "Z-Steel Arrow",
            52: "Purple-Winged Dragon",
            53: "Sacred-Blood Copper-Toothed Beast",
            60: "Golden-Horned Shura",
            67: "Mutant Golden-Sawfish",
            68: "Mutant Golden-Sawfish Spear",
            70: "Inferior to a Cat",
            74: "S-Class Saint Hall License",
            83: "One-Minute Fight",
            95: "Evolver-3",
            246: "Doppelgänger Beast Soul",
            305: "Beast Soul Add-On",
            485: "Hope in Despair"
        }
        title = str(switcher[chapterNum])
    else:
        title = str(title)
        if "Sacredblood" in title:
            title = str(title.replace("Sacredblood","Sacred-Blood"))

    return title

def vog(chapter_number, chapter_text_string):
    chapter_number = int(chapter_number)
    chapter_text = str(chapter_text_string)
    blockquote_regex = [r"\n(^\".*?killed.*?beast soul.*?point.*?\")$", r"\n(^\".*?flesh.*?point.*?\")$", r"\n(^\".*?Xenogeneic.*?hunted.*?gene.*?\")$", r"\n(^\".*?hunted.*?:.*?beast soul.*?\")$", r"\n(^\".*?killed.*?beast soul.*?inedible.*?\")$", r"\n(^\".*?beast soul.*?:.*?\")$", r"\n(^\".*?beast soul.*?;.*?\")$", r"\n(^\".*?:.*?gene lock.*?\")$", r"\n(^\".*?gene.*?\+\d+.*?\")$", r"\n(^\".*?hunted.*?found.*?.*?\")$", r"\n(^\".*?body.*?evol.*?success.*?\")$", r"\n(^\".*?consumed.*?geno point.*?\")$",
                        r"\n(^\".*?;.*?status.*?\")$", r"\n(^\".*?retrieve.*?beast soul.*?from.*?\")$", r"\n(^\".*?obtained.*?random.*?\")$", r"\n(^\".*?absorb.*?geno point.*?\")$", r"\n(^\".*?announce.*?:.*?\")$", r"\n(^\".*?eaten\..*?geno point.*?\")$", r"\n(^\".*?egg broken.*?identi.*?\")$", r"\n(^\".*?Identifying.*?beast soul.*?\")$", r"\n(^\".*?beast soul.*?identi.*?gained.*?\")$", r"\n(^\".*?killed.*?beast soul.*?life essence.*?\")$", r"\n(^\".*?evolution.*?super body.*?\")$"]
    matches = []
    addToSamples = False
    for regex in blockquote_regex:
        matches = re.findall(regex, chapter_text, re.I | re.M)
        if matches:
            for match in matches:
                block = str('> ' + match)
                block = block.title()
                chapter_text = re.sub(match, block, chapter_text, re.I, re.M)
            duplicate_regex = r'^(> > )\"'
            duplicate_results = re.findall(
                duplicate_regex, chapter_text, re.I | re.M)
            if duplicate_results:
                for x in duplicate_results:
                    rep_str = r'> '
                    chapter_text = re.sub(
                        x, rep_str, chapter_text, re.I | re.M)
            addToSamples = True
    # If VoG was found, update JSON samples
    if addToSamples == True:
        addToSample(chapter_number, 'block')
    return chapter_text

def comment_out_lines(lines, table):
    lines = lines.splitlines()
    count = len(lines)
    for x, line in enumerate(lines, start=1):
        if x < count:
            line = '\n<!-- ' + line + ' -->'
            table = str(table + line)
        else:
            line = '\n<!-- ' + line + ' -->\n'
            table = str(table + line)
    table = table.replace('<!--  -->\n', '')
    return table

def geno_r(chapter_number, chapter_text_string):
    chapter_text = str(chapter_text_string)
    geno_r_regex = r'(.*?.evol.*?:.*)$'
    geno_r_results = re.search(geno_r_regex, chapter_text, re.I | re.M)
    if geno_r_results:
        table = '<table class="geno-r">\n\t<tr>\n\t\t<th colspan="2">Geno Points</th>\n\t</tr><tr>\n\t\t<td>Required to Evolve</td>\n\t\t<td>REQUIRE</td>\n\t</tr>\n</table>'''
        geno_r_results = geno_r_results.group()
        require_regex = r'.*?(\d+).*$'
        require = re.findall(require_regex, geno_r_results)
        if require:
            require = require[0]
            table = table.replace('REQUIRE', require)
        else:
            table = table.replace('REQUIRE', 'Unknown')
        table = comment_out_lines(geno_r_results, table)
        chapter_text = chapter_text.replace(geno_r_results, table)
        addToSample(chapter_number, 'geno-r')
    return chapter_text

def get_chapter(chapter, chapter_title, chapter_url):
    # Initial Variables
    chapter_number = int(chapter)
    lines = []
    title_prefix = "Super Gene Chapter "
    title_suffix = " Online | BestLightNovel.com"

    # Chrome Webdriver
    PATH = DRIVERS_PATH
    options = ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(PATH, options=options)

    # Get Chapter Page
    driver.get(chapter_url)

    # Get article title
    article_title = driver.title
    article_title = str(article_title)
    article_title = article_title.replace(
        title_prefix, '').replace(title_suffix, '')

    try:
        settings_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "SETTING"))
        )
        settings_button.click()

        change_bad_words_button = driver.find_element_by_xpath(
            '//*[@id="trang_doc"]/div[6]/div[1]/div[2]/ul/li[5]/a')
        change_bad_words_button.click()
        try:
            chapter_text = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "vung_doc"))
            )
            chapter_text = driver.find_element_by_id("vung_doc")
            paragraphs = chapter_text.find_elements_by_tag_name("p")
            chapter_text = ''
            for paragraph in paragraphs:
                chapter_text = str(chapter_text + paragraph.text + '\n\n')

            # Strip erronious whitespace characters
            chapter_text = chapter_text.strip()

            # Save chapter text to chapters directory as text file
            filename = str('/chapter-' + chapter.zfill(5) + '.txt')
            filepath = str(CHAPTERS_DIR + filename)
            with open(filepath, 'w', encoding='utf-8') as infile:
                infile.write(chapter_text)

            # Update index.saved
            filepath = INDEX_PATH
            with open(filepath, 'r', encoding='utf-8') as infile:
                toc = load(infile)

            toc['saved'] = chapter_number
            with open(filepath, 'w') as outfile:
                dump(toc, outfile, indent=4, sort_keys=True)
        except:
            print(
                '\n\n\nError 404\nUnable to locate chapter_text on page. Quiting Script.\n')
    finally:
        driver.quit()
    return chapter_text  # End of Chapter Text

def getParsedFilepath(chapter):
    chapter = str(chapter)
    filename = "/chapter-" + chapter + ".md"
    filepath = str(MD_DIR + filename)
    return filepath

def parsedToMD(doc):
    chapter = str(doc.chapter)
    meta = doc.meta
    head = doc.head
    text = doc.text

    md_text = str(meta + head + text)
    filepath = getParsedFilepath(chapter)
    with open(filepath, 'w') as outfile:
        outfile.write(md_text)

def badWords(chapter_text):
    badWords = {
        "shit1": {
            "regex": r's(\W\W)t',
            "replacement": "hi"
        },
        "shit2": {
            "regex": r'sh(\W)t',
            "replacement": "i"
        },
        "fuck": {
            "regex": r'f(\W\W)k',
            "replacement": "uc"
        },
        "ass": {
            "regex": r'a(\W\W)\s|a(\W\W)[\.\!\-\?]|a(\W\W)hole',
            "replacement": 'ss'
        },
        "asshole": {
            "regex": r'(\W{4})le',
            "replacement": 'ssho'
        }
    }
    keys = badWords.keys()
    for key in keys:
        regex = badWords[key]['regex']
        replacement = badWords[key]['replacement']
        chapter_text = re.sub(regex, replacement, chapter_text, re.I)
    return chapter_text

def needsReview(chapter_number, chapter_text,):
    chapter_text = str(chapter_text)
    chapter_number = int(chapter_number)
    chapter = str(chapter_number)
    filepath = str('needs_review/chapter-' + chapter.zfill(5) + '.md')
    with open(filepath, 'w') as outfile:
        outfile.write(chapter_text)  # End of Needs Review

def addToSample(chapter, sample_group):
    chapter = int(chapter)
    sample_group = str(sample_group)
    samplesPath = str('JSON/samples.json')
    with open(samplesPath, 'r') as infile:
        samples = load(infile)
    # If samples dictionary exists:
    if samples:
        # Gey keys from sample dictionary
        keys = samples.keys()
        if sample_group in keys:
            # Use a temp 'set' to ensure no duplicate entries
            existingSamples = set((samples[sample_group]))
            existingSamples.add(chapter)
            # Parse temp set into list
            samplesList = []
            for x in existingSamples:
                samplesList.append(x)
            # Add sample to sample group
            samples[sample_group] = samplesList
        else:
            # If sample group is not found, create it
            samples[sample_group] = [chapter]
    else:
        # If samples is not found, create it
        samples = {}
        samples[sample_group] = [chapter]

    with open(samplesPath, 'w') as outfile:
        dump(samples, outfile)  # End of addToSamples()

def status(chapter, chapter_text):
    chapter_text = str(chapter_text)
    chapter = str(chapter)
    chapter_number = int(chapter)
    status_regex = r'(.*?^Han Sen:.*$\n\n.*?^Status.*$\n\n.*?^Life.*)$|(.*?^Han Se:.*$\n\n.*?^Super.*$\n\n.*?^Status.*$\n\n.*?^Life.*)$|(.*?^Han Sen.*$\n\n.*?^Stage.*$\n\n.*?^Life.*)$|(.*?^Han Sen.*$\n\n.*?^Level.*$\n\n.*?^Life.*)$'

    # Find, Eveluate, Comment-out, Create, & Replace with Table
    status_search_results = re.search(
        status_regex, chapter_text, re.IGNORECASE | re.MULTILINE)
    if status_search_results:
        status = status_search_results.group()
        status_no_punc = status.replace(':', '').replace(
            '-', '').replace('–', '').replace('.', '')
        regex_life = r'(.*?Life.*)$'
        lifespan = re.search(regex_life, status_no_punc, re.I)
        if lifespan:
            try:
                lifespan = lifespan.group()
                lifespan = re.search(r'\d+', lifespan)[0]
                lifespan = int(lifespan)
            except:
                lifespan = lifespan.lower()
                if 'six' in lifespan:
                    lifespan = 600
                elif 'five' in lifespan:
                    lifespan = 500
                elif 'four' in lifespan:
                    lifespan = 400
                elif 'three' in lifespan:
                    lifespan = 300
                else:
                    lifespan = 200

            if lifespan == 600:
                status_dict = {
                    'Status': 'God',
                    'Geno Body': 'Not Created',
                    'Lifespan': '600 years'
                }
            elif lifespan == 500:
                status_dict = {
                    'Status': 'Demigod',
                    'Super Body': 'Super King Spirit - Ultimate',
                    'Lifespan': '500 years'
                }
            elif lifespan == 400:
                status_dict = {
                    'Status': 'Surpasser',
                    'Super Body': 'Super King Spirit',
                    'Lifespan': '400 years'
                }
            elif lifespan == 300:
                status_dict = {
                    'Status': 'Evolver',
                    'Super Body': 'King Spirit',
                    'Lifespan': '300 years'
                }
            else:
                status_dict = {
                    'Status': 'Unevolved',
                    'Lifespan': '200 years'
                }
        else:
            print('Lifespan not found in status results. Exiting Script')

        # Create Status Table
        table = '<table class="status">\n\t<tr>\n\t\t<th colspan="2">Han Sen</th>\n\t</tr>'
        keys = status_dict.keys()
        for key in keys:
            td_lable = str(key)
            td_value = str(status_dict.get(key))
            table_row = str('<tr>\n\t\t<td>' + td_lable +
                            '</td>\n\t\t\t<td>' + td_value + '</td>\n\t\t</tr>')
            table = str(table + table_row)
        table = str(table + '\n</table>')

        # Comment out status text
        status = str(status)
        table = comment_out_lines(status, table)

        # Replace Status text with HTML Status Table and HTML Commented Lines
        chapter_text = chapter_text.replace(status, table)
        addToSample(chapter_number, 'status')
    return chapter_text

def getOutfile(chapter):
    chapterNum = int(chapter)
    rem = chapterNum % 1000
    dictNum = ((chapterNum - rem)/1000) + 1
    outfile = str('JSON/supergene' + dictNum + '.json')
    return outfile

def pushcutsPost(newChapterList):
    numOfNewChpaters = len(newChapterList)
    if numOfNewChpaters == 1:
        apiDict = newChapterList[0]
        apiText = apiDict['apiText']
        chapter_text = apiDict['text']
        body_dict = {
            "text": apiText,
            "title": "New Chapter!",
            "image": "https://imgur.com/fJvp5Ns",
            "defaultAction": {
                "name": "Read Now",
                "input": chapter_text,
                "shortcut": "Read it Now"
            }
        }
    else:
        # Function Vars
        apiDict = []
        apiText = []
        chapter_text = []
        for dictionary in newChapterList:
            apiDict = dictionary
            text = apiDict['text']
            chapter_text.append(text)
            apiText.append(str(apiDict["apiText"]))
        apiText = '\n'.join(apiText)
        chapter_text = '\n\n---\n\n'.join(chapter_text)
        body_dict = {
            "text": apiText,
            "title": "New Chapters!",
            "image": "https://imgur.com/fJvp5Ns",
            "defaultAction": {
                "name": "Read Now",
                "input": chapter_text,
                "shortcut": "Read it Now"
            }
        }
    url = "https://api.pushcut.io/Jp1W4E3lqPYZKQw6o7l-j/notifications/New%20Chapter"
    headers = "Content-Type: application/json"
    payload = dumps(body_dict, indent=4, sort_keys=True)
    auth = requests.auth.HTTPBasicAuth("API-Key: pOkqopW3cKXf7Fu-em1KCPsL")

    result = requests.post(url=url, headers=headers, data=payload, auth=auth)
    log.debug(result)
# End of user defined functions -----------------

# Get Table of COntents
get_toc()
log.debug("Updated Table of Contents")

# Open Toc
with open(TOC_PATH, 'r') as infile:
    toc = load(infile)

# Open index
with open(INDEX_PATH, 'r') as infile:
    index = load(infile)

# Script vars
count = int(index['count'])
saved = int(index['saved'])
keys = toc.keys()
chapters = []

# get chapters from toc keys
for key in keys:
    chapter_number = int(key)
    if chapter_number > saved:
        chapter = str(key)
        chapters.append(chapter)

if chapters:
    apiList = []
    newChapterCount = len(chapters)
    if newChapterCount == 1:
        print(str(newChapterCount) + ' new chapter found.')
        log.info('1 new chapter found.')
    else:
        print(str(newChapterCount) + ' new chapters found.')
        log.info(str(newChapterCount) + ' new chapters found.')

    # Establishing a Connection
    atlas()

    # Get new chapter(s)
    for chapter in tqdm(chapters, ncols=100, unit='ch'):
        title = str(toc[chapter]['title'])
        url = str(toc[chapter]['url'])
        chapter_text = get_chapter(chapter, title, url)
        chapterNum = int(chapter)
        # Generate Markdown Head
        meta = "Title:" + title + "\nChapter:" + chapter + "\nCSS:sg.css\n\n"
        atx = "### " + title + "\n#### Chapter " + chapter + "\n\n",
        image = "![](gem.gif)"
        head = meta + atx + image

        # Generate Chapter Document
    new_chapter = Chapter(
        chapter = chapterNum,
        title = title,
        original_text = chapter_text,
        text = "",
        final_text = "",
        url = url,
        css = "sg.css",
        tags = [],
        added = datetime.datetime.now,
        markdown_meta = meta,
        atx = atx,
        image = "![](gem.gif)",
        head = head,
        section = 6,
        book = 5
    )

    new_chapter = db_parse_chapter(new_chapter)
    new_chapter.save()

    log.info('Added Chapter ' + chapter + ' to supergeneDB')

else:
    print('No new chapters available.\n\nLatest Chapter: ' + str(count))
    log.debug('No new chapters are available.')
