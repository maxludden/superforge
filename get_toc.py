# utilities/get_toc.py:

import re
import sys
from json import load, dump

from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv

from core.log import errwrap, log
from core.atlas import sg, BASE, max_title
from core.chapter import Chapter, generate_section, generate_book

DRIVER_PATH = 'driver/chromedriver'
RUN_PATH = 'json/run.json'
TOC_PATH = 'json/toc.json'
TOC_URL = 'https://bestlightnovel.com/novel_888112448'

@errwrap()
def get_last_run():
    '''
    Retrieve the last_run from the run.json file.

    Returns:
        `last_run` (int): 
            The last_run integer from the run.json file.
    '''
    with open(RUN_PATH, 'r') as f:
        run_dict = dict((load(f)))
        last_run = run_dict['last_run']
    return last_run
    
@errwrap()
def increment_run(last_run: int):
    '''
    Increments the last_run.

    Args:
        `last_run` (int):
            The last recorded run.
    
    Returns:
        `current_run` (int):
            The current run.
    '''
    current_run = last_run + 1
    return current_run
    
@errwrap()
def update_run(current_run: int):
    '''
    Updates the run.json file with the current run.

    Args:
        `current_run` (int):
            The current run.
    '''
    with open(RUN_PATH, 'w') as f:
        dump({'last_run': current_run}, f)
        
@errwrap()
def new_run():
    '''
    Retrieves the last_run, increments it, and updates the run.json file.
    '''
    last_run = get_last_run()
    current_run = increment_run(last_run)
    update_run(current_run)
    return current_run

@errwrap()
def get_soup(url: str):
    '''
    Retrieves the soup for the given url.

    Args:
        `url` (str):
            The url to retrieve the soup for.

    Returns:
        `soup` (bs4.BeautifulSoup):
            The soup for the given url.
    '''
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup

@errwrap()
def get_list_chapter(soup: BeautifulSoup):
    '''
    Retrieves the list_chapter from the soup.

    Args:
        `soup` (bs4.BeautifulSoup):
            The soup to retrieve the list_chapter from.

    Returns:
        `list_chapter` (bs4.element.Tag):
            The list_chapter element.
    '''
    results = soup.find(id="list_chapter")
    return results

@errwrap()
def get_links(list_chapter: BeautifulSoup):
    '''
    Retrieves the links from the list_chapter.

    Args:
        `list_chapter` (bs4.element.Tag):
            The list_chapter element.

    Returns:
        `links` (bs4.element.ResultSet):
            The links element.
    '''
    links = list_chapter.find_all("a")
    return links
    
@errwrap()
def get_link_text(line: BeautifulSoup):
    '''
    Retrieves the link text from the line.

    Args:
        `line` (bs4.element.Tag):
            The line element.

    Returns:
        `link_text` (str):
            The link text.
    '''
    link_text = line.text
    link_text = link_text.strip()
    return link_text
    
    
@errwrap()
def get_chapter(link_text: str):
    '''
    Retrieves the chapter from the link.

    Args:
        `link` (bs4.element.Tag):
            The link element.

    Returns:
        `chapter` (int):
            The chapter number.
    '''

    chapter = int(re.findall(r'\d+', link_text)[0])
    return chapter

@errwrap()
def fix_hyphen(toc1_title: str, toc2_title: str) -> str:
    """
    Fix mismatch between toc1 and toc2
    """
    no_hyphens = toc1_title.replace("-", "")
    if no_hyphens.lower() == toc2_title.lower():
        return toc1_title

@errwrap() 
def add_t(toc1_title: str, toc2_title: str) -> str:
    """
    Add t to toc1_title if it is missing
    """
    t_title = f"{toc2_title}t"
    if toc1_title.lower() == t_title.lower():
        return toc1_title


@errwrap()
def get_toc():
    '''
    Generate Table of Contents from URL and write it to json file on disk
    '''
    #> Retrieve Titles from MongoDB
    with open ("json/toc1.json", 'r') as infile:
        toc1 = dict((load(infile)))
    
    #> Get Soup from URL
    soup = get_soup(TOC_URL)
    list_chapter = get_list_chapter(soup)
    links = get_links(list_chapter)

    #> Declare Data Structure for new TOC
    toc2 = {}
    mismatch  = []
    
    # > Loop through links returned from URL
    for x, link in enumerate(links, start=1):
        link_text = str(link.text).strip()
        chapter = re.findall(r"\d+", link_text)[0]  # get chapter
        toc1_title = toc1[chapter]['title']         # get title from toc1
        
        #> Parse title from link
        initial_title = link_text.split(chapter)[1]
        if ":" in initial_title:
            initial_title = initial_title.replace(":", "").strip()
        if "-" in initial_title:
            initial_title = initial_title.replace("-", "").strip()
        initial_title = initial_title.strip()
        title = max_title(initial_title)
        
        #> Parse Titles
        if title == "":
            title = toc1_title
        if x == 39:
            chapter = "39"
            title = "Saint Paul: Part 1"
        if x == 40:
            chapter = "40"
            title = "Saint Paul: Part 2"
        match int(chapter):
            case 17|39|40|2204|2392|3269|3343|3462:
                title = toc1_title
            case _:
                pass
        
        #> Determine if title matches existing toc
        if toc1_title == title:
            match = True
        else:
            match= False 
        
        #> If title doesn't match, try to fix it
        if match == False:
            # add hyphen to title if it is missing
            fixed_hyphen_title = fix_hyphen(toc1_title, title)
            if fixed_hyphen_title == toc1_title:
                match = True
                title = toc1_title
            
            # add a "t" to the end of the title if it is missing
            add_t_title = add_t(toc1_title, title)
            if add_t_title == toc1_title:
                match = True
                title = toc1_title
        
        #> Capitalize the word after a hyphen in the title 
        if "-" in title:
            title_split = title.split()
            new_title = []
            for word in title_split:
                if "-" in word:
                    word_split = word.split("-")
                    capitalized_split = [word.capitalize() for word in word_split]
                    word = "-".join(capitalized_split)
                new_title.append(word)
            
            title = " ".join(new_title)
            
        # > Get URL from link
        link_url = link["href"]

        chapter_dict = {
            "chapter": chapter,
            "title": title,
            "url": link_url
        }
        if match == False:
            mismatch.append(chapter_dict)
            
        toc2[chapter]=chapter_dict

    with open ("json/toc2.json", 'w') as outfile:
        dump(toc2, outfile, indent=4)
    with open ("json/mismatch.json", 'w') as outfile:
        dump(mismatch, outfile, indent=4)

    log.info(f"Wrote toc2.json to disk.")
