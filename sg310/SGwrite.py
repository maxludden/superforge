# SGwrite.py

# Dependencies
from SG import (
    Chapter, 
    Section,
    atlas,
    get_text
    )
from datetime import datetime
from tqdm.auto import tqdm
from json import load, dump
from markdown2 import markdown
import logging
import sys
import re

def write_chapter(ch):
    for doc in Chapter.objects(chapter=ch):
        chapter = str(ch)
        text = get_text(doc)
        filepath = "chapters/" + chapter + ".md"
        with open(filepath, "w") as chapter_text:
            chapter_text.write(text)
    print("Wrote Chapter " + chapter + " to file.")
     
def output(doc):
    final_text = doc.final_text
    if final_text != "":
        text = final_text
    else:
        text = doc.text
    head = doc.head
    chapter_text = str(head + text)

    chapter = str(doc.chapter)
    chapterNum = int(chapter)
    if chapterNum < 425:
        section = "1"
    elif chapterNum < 883:
        section = "2"
    elif chapterNum < 1339:
        section = "3"
    elif chapterNum < 1680:
        section = "4"
    elif chapterNum < 1712:
        section = "5"
    else:
        section = "6"
    filename = str("chapter-" + chapter.zfill(5) + ".md")
    filepath = str("/" + filename)
    with open(filepath, "w") as outfile:
        outfile.write(chapter_text)
        
def write_chapters(book):
    book = str(book)
    atlas()
    DRAFTS = "JSON/drafts.json"
    with open(DRAFTS, "r") as infile:
        draft_dict = dict((load(infile)))
    book_dict = draft_dict[book]
    chapters = book_dict["chapters"]

    for chapter in tqdm(chapters):
        for doc in Chapter.objects(chapter=chapter):
            chapter = str(doc.chapter)
            filename = "chapter-" + chapter.zfill(5) + ".html"
            html_dir = "/Users/Max/Dev/SG3.10/Drafts/book5/html/"
            filepath = html_dir + filename
            html = doc.html
            with open(filepath, "w") as outfile:
                outfile.write(html)

# SG.py

# Dependencies
from mongoengine import Document, connect, disconnect_all
from main import Chapter, Section
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
CHAPTERS_JSON = "JSON/chapters.json"
CHAPTERS_DIR = "chapters/"
LOG_PATH = "logs/db_main.log"


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

# Parsing Functions
def get_text(doc):
    final_text = doc.final_text
    if final_text != "":
        text = final_text
    else:
        text = doc.text

    return str(text)

def remove_ch_title(doc):
    chapter = str(doc.chapter)
    text = get_text(doc)
    title = max_title(doc.title)
    if chapter in text:
        split_text = text.split("\n\n")
        updated_text = "\n\n".join(split_text[1::])
        doc.final_text = updated_text
        doc.save()
        lp(
            "Fixed Chapter "
            + chapter
            + "\n\tChapter Head: "
            + chapter
            + " "
            + title
            + "\n\tRemoved Line: "
            + split_text[0]
        )
        
def badWords(text, chapter):
    chapter = str(chapter)
    badWords = {
        "shit1": {"regex": r"sh\*t", "replacement": "shit"},
        "shit2": {"regex": r"s\*#t", "replacement": "shit"},
        "fuck1": {"regex": r"f\*#k", "replacement": "uc"},
        "shit3": {"regex": r"Sh\*t", "replacement": "Shit"},
        "shit4": {"regex": r"S\*#t", "replacement": "Shit"},
        "fuck2": {"regex": r" F\*#k ", "replacement": " Fuck "},
        "fuck3": {"regex": r" F\*ck ", "replacement": " Fuck "},
    }
    keys = badWords.keys()
    for key in keys:
        regex = badWords[key]["regex"]
        results = findall(regex, text, re.I)
        if results:
            replacement = badWords[key]["replacement"]
            for x in results:
                text = sub(regex, replacement, text, re.I)
                log.info("\n\t\t\tUpdated " + regex + " -> " + replacement)
    badWords = {
        "ass1": {"regex": r" \*ss ", "replacement": " ass "},
        "ass2": {"regex": r"\n\*ss ", "replacement": "\nAss "},
        "ass3": {"regex": r"\. \*ss ", "replacement": ". Ass "},
    }
    keys = badWords.keys()
    for key in keys:
        regex = badWords[key]["regex"]
        results = findall(regex, text)
        if results:
            replacement = badWords[key]["replacement"]
            for x in results:
                text = sub(regex, replacement, text)
    return text

def removeDotCom(text):
    text = str(text)
    dotComRegex = r"^(.*?\.com.*)$"
    results = findall(dotComRegex, text, re.I | re.M)
    if results:
        for match in results:
            text = sub(match, "", text, re.I | re.M)
    return text

# Formatting Functions
def comment_out_lines(lines, table):
    lines = lines.splitlines()
    count = len(lines)
    for x, line in enumerate(lines, start=1):
        if x < count:
            line = "\n<!-- " + line + " -->"
            table = str(table + line)
        else:
            line = "\n<!-- " + line + " -->\n"
            table = str(table + line)
    table = table.replace("<!--  -->\n", "")
    return table

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
        r"\n(^\"God.*?Evolu.*?\")$"
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

def geno_r(text):
    text = str(text)
    geno_r_regex = r"(.*?.evol.*?:.*)$"
    geno_r_results = re.search(geno_r_regex, text, re.I | re.M)
    if geno_r_results:
        table = (
            '<table class="geno-r">\n\t<tr>\n\t\t<th colspan="2">Geno Points</th>\n\t</tr><tr>\n\t\t<td>Required to Evolve</td>\n\t\t<td>REQUIRE</td>\n\t</tr>\n</table>'
            ""
        )
        geno_r_results = geno_r_results.group()
        require_regex = r".*?(\d+).*$"
        require = findall(require_regex, geno_r_results)
        if require:
            require = require[0]
            table = table.replace("REQUIRE", require)
        else:
            table = table.replace("REQUIRE", "Unknown")
        table = comment_out_lines(geno_r_results, table)
        text = text.replace(geno_r_results, table)
    return text

def status(text):
    text = str(text)
    status_regex = r"(.*?^Han Sen:.*$\n\n.*?^Status.*$\n\n.*?^Life.*)$|(.*?^Han Se:.*$\n\n.*?^Super.*$\n\n.*?^Status.*$\n\n.*?^Life.*)$|(.*?^Han Sen.*$\n\n.*?^Stage.*$\n\n.*?^Life.*)$|(.*?^Han Sen.*$\n\n.*?^Level.*$\n\n.*?^Life.*)$"

    # Find, Eveluate, Comment-out, Create, & Replace with Table
    status_search_results = re.search(status_regex, text, re.IGNORECASE | re.MULTILINE)
    if status_search_results:
        status = status_search_results.group()
        status_no_punc = (
            status.replace(":", "").replace("-", "").replace("–", "").replace(".", "")
        )
        regex_life = r"(.*?Life.*)$"
        lifespan = re.search(regex_life, status_no_punc, re.I)
        if lifespan:
            try:
                lifespan = lifespan.group()
                lifespan = re.search(r"\d+", lifespan)[0]
                lifespan = int(lifespan)
            except:
                lifespan = lifespan.lower()
                if "six" in lifespan:
                    lifespan = 600
                elif "five" in lifespan:
                    lifespan = 500
                elif "four" in lifespan:
                    lifespan = 400
                elif "three" in lifespan:
                    lifespan = 300
                else:
                    lifespan = 200

            if lifespan == 600:
                status_dict = {
                    "Status": "God",
                    "Geno Body": "Not Created",
                    "Lifespan": "600 years",
                }
            elif lifespan == 500:
                status_dict = {
                    "Status": "Demigod",
                    "Super Body": "Super King Spirit - Ultimate",
                    "Lifespan": "500 years",
                }
            elif lifespan == 400:
                status_dict = {
                    "Status": "Surpasser",
                    "Super Body": "Super King Spirit",
                    "Lifespan": "400 years",
                }
            elif lifespan == 300:
                status_dict = {
                    "Status": "Evolver",
                    "Super Body": "King Spirit",
                    "Lifespan": "300 years",
                }
            else:
                status_dict = {"Status": "Unevolved", "Lifespan": "200 years"}
        else:
            print("Lifespan not found in status results. Exiting Script")

        # Create Status Table
        table = (
            '<table class="status">\n\t<tr>\n\t\t<th colspan="2">Han Sen</th>\n\t</tr>'
        )
        keys = status_dict.keys()
        for key in keys:
            td_lable = str(key)
            td_value = str(status_dict.get(key))
            table_row = str(
                "<tr>\n\t\t<td>"
                + td_lable
                + "</td>\n\t\t\t<td>"
                + td_value
                + "</td>\n\t\t</tr>"
            )
            table = str(table + table_row)
        table = str(table + "\n</table>")

        # Comment out status text
        status = str(status)
        table = comment_out_lines(status, table)

        # Replace Status text with HTML Status Table and HTML Commented Lines
        text = text.replace(status, table)
    return text

def db_logVog(doc):
    text = doc.original_text
    chapter = str(doc.chapter)
    bq_text = vog(text)
    if bq_text != text:
        regex = r"^(> \".*?\")$"
        results = findall(regex, bq_text, re.M | re.I)
        if results:
            length = len(results)
            if length > 1:
                for x, result in enumerate(results, start=1):
                    result = str(result)
                    x = str(x)
                    resultString = str(
                        "Chapter " + chapter + ": Match " + x + ": " + result
                    )
                    print(resultString)
            elif length == 1:
                result = str(results[0])
                resultString = str("Chapter " + chapter + ": " + result)
                print(resultString)
            else:
                pass

def fixDemigod(text):
    if "demiGod" in text:
        text = text.replace("demiGod","demigod")
    if "DemiGod" in text:
        text = text.replace("DemiGod","Demigod")
    return text
                
def db_parse_chapter(doc):
    title = str(doc.title)
    chapter = str(doc.chapter)
    final_text = doc.final_text
    if final_text != "":
        doc.text = final_text
    else:
        text = str(doc.original_text)
        tags = set(([]))

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

        doc.text = text

        # Fix Jadeskin
        jadeskin_results = findall("jadeskin", text)
        if jadeskin_results:
            for result in jadeskin_results:
                text = sub(result, "Jadeskin", text)

        # Fix tags
        etags = set((doc.tags))
        tags = []
        for tag in etags:
            tags.append(tag)
        doc.tags = tags
        
    doc.save()
    lp("Parsed Chapter " + chapter)
    return doc  # End of parse_chapter

def addSection(doc):
    chapter = int(doc.chapter)
    # Determine Secrtion from Chapter
    if chapter < 425:
        section = 1
    elif chapter < 883:
        section = 2
    elif chapter < 1339:
        section = 3
    elif chapter < 1680:
        section = 4
    elif chapter < 1712:
        section = 5
    elif chapter < 1961:
        section = 6
    elif chapter < 2205:
        section = 7
    elif chapter < 2244:
        section = 8
    elif chapter < 2640:
        section = 9
    elif chapter < 2794:
        section = 10
    elif chapter < 3034:
        section = 11
    else:
        section = 12
    doc.section = section
    return doc

def get_section(chapter):
    chapter = int(chapter)
    # Determine Secrtion from Chapter
    if chapter < 425:
        section = 1
    elif chapter < 883:
        section = 2
    elif chapter < 1339:
        section = 3
    elif chapter < 1680:
        section = 4
    elif chapter < 1712:
        section = 5
    elif chapter < 1961:
        section = 6
    elif chapter < 2205:
        section = 7
    elif chapter < 2244:
        section = 8
    elif chapter < 2640:
        section = 9
    elif chapter < 2794:
        section = 10
    elif chapter < 3034:
        section = 11
    else:
        section = 12
    return section

def addBook(doc):
    section = doc.section
    books = {1: 1, 2: 2, 3: 3, 4: 4, 5: 4, 6: 5}
    book = books[section]
    doc.book = book
    return doc

def get_book(section):
    books = {1: 1, 2: 2, 3: 3, 4: 4, 5: 4, 6: 5, 7: 6, 8: 7, 9: 8}
    book = books[section]
    return book

def make_html(doc):
    chapter = str(doc.chapter)
    title = doc.title
    css = "../Styles/sg.css"
    text = get_text(doc)
    md_text = markdown(text)
    atx = "### " + title + "\n\n####Chapter " + chapter + "\n\n"
    atx_md = markdown(atx)
    md = atx_md + "\n\n" + doc.image + "\n\n" + md_text

    html_head = '<?xml version="1.0" encoding="utf-8"?>\n'
    html_head += "<!DOCTYPE html>\n\n"
    html_head += '<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xmlns:epub="http://www.idpf.org/2007/ops">\n'
    html_head += "<head>\n"
    html_head += '  <meta charset="utf-8"/>\n'
    html_head += "  <title>" + title + "</title>\n"
    html_head += '  <meta name="chapter" content="' + chapter + '"/>\n'
    html_head += '  <link type="text/css" rel="stylesheet" href="' + css + '"/>\n'
    html_head += "</head>\n\n"
    html_head += "<body>\n\n"
    html = html_head + md + "\n\n</body>\n\n"
    doc.html = html
    doc.save()
