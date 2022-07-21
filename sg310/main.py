# main.py
# Dependancie
from enum import unique
import gc
import logging
import re
from runpy import _ModifiedArgv0
import sys
from datetime import datetime
from json import dump, load

from bs4 import BeautifulSoup
from markdown2 import markdown as md
from mongoengine import Document, connect, disconnect_all,register_connection
from mongoengine.fields import (BooleanField, DateTimeField, IntField,
                                ListField, StringField, URLField, LazyReferenceField)
from mongoengine.context_managers import switch_db, switch_collection
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm.auto import tqdm
from requests import get

DRIVERS_PATH = "Driver/chromedriver"
INDEX_PATH= 'JSON/index.json'

# Declair project paths as constsants
CH_INDEX = "JSON/chapter_index.json"
TOC_PATH = "JSON/toc.json"
SAMPLES_PATH = "JSON/samples.json"
CHAPTER_JSON = "JSON/chapter.json"
SECTION_JSON = "JSON/section.json"
INDEX_PATH = "JSON/index.json"
LOG_PATH = "logs/db_main.log"
DRIVERS_PATH = "Driver/chromedriver"
GEM_IMG_URL = '<img src="https://i.imgur.com/FhWsZat.gif" alt="Spinning Black Gem" widtj="120" height="67.5" />\n\n'
MISSING = [0,3095,3117]   
BOOKS = {1:1,2:2,3:3,4:4,5:4,6:5,7:6,8:6,9:7,10:7,11:8,12:9}

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


# Log & Print Function
def lp(msg):
    msg = str(msg)
    log.info(msg)
    print(msg)

# Connect to MongoDB Atlas 
def atlas_lp():    # Connect to Atlas using LP
    # Read Auth Credentials from file
    with open("JSON/authkey.json", 'r') as infile:
        atlas_authkey = dict((load(infile)))
    URI = atlas_authkey["atlas"]["uri"]

    disconnect_all()
    lp("Connecting to Atlas MongoDB Cluster...")
    try:
        connect("supergene", host=URI)
        lp("\tSuccess!\n\t\tHost: cluster0.7yzr5.mongodb.net")
        lp("\t\tUsing Supergene Database")
    except:
        lp("Unable to connect to Atlas Cluster...")
        lp("\t\tQuiting Script.")

def atlas():        #  log.info
    # Read Auth Credentials from file
    with open("JSON/authkey.json", 'r') as infile:
        atlas_authkey = dict((load(infile)))
    URI = atlas_authkey["atlas"]["uri"]

    disconnect_all()
    log.info("Connecting to Atlas MongoDB Cluster...")
    try:
        connect("supergene", host=URI)
        log.info("\tSuccess!\n\t\tHost: cluster0.7yzr5.mongodb.net")
        log.info("\t\tUsing Supergene Database")
    except:
        log.info("Unable to connect to Atlas Cluster...")
        log.info("\t\tQuiting Script.")


def connect_old():
    with open ("JSON/authkey.json", 'r') as json:
        auth = dict((load(json)))
    supergene = auth["supergene"]
    
    lp("Connecting to Atlas MongoDB Cluster..."
       )
    try:
        connect("sg",host=supergene)
        lp("\tSuccess!\n\t\tHost: cluster0.7yzr5.mongodb.net")
        lp("\t\tUsing Supergene Database")
        
        lp("Defining Documents...")
        class Chapter(Document):
            chapter = IntField(Required=True, unique=True)
            title = StringField(Required=True, max_length=200)
            original_text = StringField(Required=True)
            text = StringField()
            final_text = StringField()
            url = URLField(Required=True)
            css = StringField(max_length=200)
            tags = ListField(StringField(max_length=50), default=list)
            added = DateTimeField(default=datetime.now)
            image = StringField(max_length=200)
            head = StringField(max_length=800)
            section = IntField()
            book = IntField()
            atx = StringField(max_length=500)
            html = StringField()
            edited = BooleanField()

        class Section(Document):
            title = StringField(Required=True, max_length=200)
            section = IntField(Required=True, unique=True)
            css = StringField(max_length=200)
            header3 = StringField(max_length=300)
            image = StringField(max_length=200)
            text = StringField()
            filename = StringField()
            body = StringField()
            book = IntField()
            atx = StringField(max_length=300)
            ch_start = IntField()
            ch_end = IntField()
            chapters = ListField(IntField())
            
        lp("Defined Section and Chapter Document Schemas.")
    except:
        log.info("Unable to connect to Atlas Cluster...")
        log.info("\t\tQuiting Script.")
    
def connect_sg():
    with open ("JSON/authkey.json", 'r') as json:
        auth = dict((load(json)))
    sg = auth["sg"]
    
    try:
        connect("sg",host=sg)
        lp("\tSuccess!\n\t\tHost: cluster0.7yzr5.mongodb.net")
        lp("\t\tUsing SG Database")
        
        lp("Defining Documents...")
        class Book(Document):
            _id = IntField(primary_key=True)
            book = IntField(Required=True, unique=True)
            title = StringField(Required=True, max_length=500)
            output = StringField()
            cover = StringField()
            cover_path = StringField()
            uuid = StringField()
            default = StringField()
            start = IntField()
            end = IntField() 

        class Section(Document):
            _id = IntField(primary_key=True)
            section = IntField(Required=True, unique=True)
            title = StringField(Required=True, max_length=250)
            html = StringField()
            start = IntField()
            end = IntField()
            book = LazyReferenceField(Book)
            
        class Chapter(Document):
            chapter = IntField(primary_key=True)
            title = StringField(max_length=200, Required=True)
            text = StringField()
            html = StringField()
            tags = ListField(StringField(max_length=50))
            section = LazyReferenceField(Section)
            book = LazyReferenceField(Book)
            created = DateTimeField(default=datetime.now())
            modified = DateTimeField(default=datetime.now())
            
        lp("Defined Book, Section, and Chapter Document Schemas.")
        
    except:
        log.info("Unable to connect to Atlas Cluster...")
        log.info("\t\tQuiting Script.")
    
# Defining Documents




# Get text from Document
def get_text(doc):
    final_text = doc.final_text
    if final_text != "":
        text = final_text
    else:
        text = doc.text
    return str(text)

# Retrieve Atlas Loggin
def atlas_auth(*key):
    with open("JSON/authkey.json", 'r') as infile:
        atlas_authkey = dict((load(infile)))
    if key:
        match key:
            case "user":
                return atlas_authkey["user"]
            case "password":
                return atlas_authkey["password"]
            case "uri":
                return atlas_authkey["uri"]
            case "uri_":
                return atlas_authkey["uri_"]
            case _:
                print("Error: Key not found.")
    else:
        return atlas_authkey

# Connect to MongoDB (Local)
def connect_local():
    disconnect_all()
    lp("Connecting to MongoDB's local server...")
    try:
        connect("supergene", host="mongodb://localhost", port=27017)
        lp("\tSuccess!\n\t\tHost: mongodb://127.0.0.1:27017")
        lp("\t\tUsing Supergene Database")
    except:
        lp("Unable to connect to the MongoDB server on localhost...")
        lp("\t\tQuiting Script.")

# Custom string Title Case Method
def max_title(title):
    title = str(title).lower()
    articles = ['a','an','and','as','at','but','by','en','for','if','in','nor','of','on','or','per','the','to','vs']
    word_list = re.split(" ", title)
    final = [word_list[0].capitalize()]
    for word in word_list[1:]:
        final.append(word if word in articles else word.capitalize())
    result = " ".join(final)
    return str(result)

def print_title(msg):                      
    title = max_title(msg)
    print(title)

# def get_chapter(chapter: int) -> str:
#     # Initial Variables
#     chapter = int(chapter)
#     lines = []
#     title_prefix = "Super Gene Chapter "
#     title_suffix = " Online | BestLightNovel.com"

#     # Chrome Webdriver
#     selenium.webdriver.chrome.webdriver.WebDriver(
#         executable_path='Driver/chromedriver', 
#         port=0,
#         options=None, 
#         service_args=None, 
#         desired_capabilities=None, 
#         service_log_path=None, 
#         chrome_options=None, 
#         keep_alive=True
#         )

#     options = ChromeOptions()
#     options.add_argument("--headless")
#     driver = webdriver.Chrome(DRIVERS_PATH, options=options)

#     # Get Chapter Page
#     with open ("JSON/toc.json", 'r') as infile:
#         toc = dict((load(infile)))
#     url = toc[str(chapter)]["url"]
#     driver.get(url)

#     # Get article title
#     article_title = driver.title
#     article_title = article_title.replace(
#         title_prefix, '').replace(title_suffix, '')

#     try:
#         settings_button = WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.LINK_TEXT, "SETTING"))
#         )
#         settings_button.click()

#         change_bad_words_button = driver.find_element_by_xpath(
#             '//*[@id="trang_doc"]/div[6]/div[1]/div[2]/ul/li[5]/a')
#         change_bad_words_button.click()
#         try:
#             text = WebDriverWait(driver, 10).until(
#                 EC.presence_of_element_located((By.ID, "vung_doc"))
#             )
#             text = driver.find_element_by_id("vung_doc")
#             paragraphs = text.find_elements_by_tag_name("p")
#             text = ''
#             for paragraph in paragraphs:
#                 text = str(text + paragraph.text + '\n\n')

#             # Strip erronious whitespace characters
#             text = text.strip()

#             # Save chapter text to chapters directory as text file
#             filepath = "chapters/" + str(chapter).zfill(5) + ".md"
#             with open(filepath, 'w', encoding='utf-8') as outfile:
#                 outfile.write(text)
#         except:
#             print(
#                 '\n\n\nError 404\nUnable to locate text on page. Quiting Script.\n')
#     finally:
#         driver.quit()
#     return text  # End of Chapter Text


def get_html(self, chapter, title):
    head = get_ch_head(chapter,title)
    body = md(self.md_text)
    body += "\n\n</body>"
    html = head + body
    return html

def update_html(doc):
    # Get data from DB
    text = get_text(doc)
    title = doc.title
    chapter = str(doc.chapter)
    img = doc.image
    css = doc.css
    head = get_ch_head(title, chapter) # Generate HTML Heading
    body = "### " + max_title(title) + "\n\n####Chapter " + chapter + "\n\n" + img + "\n\n" + text
    body = md(body)
    html = head + body + "\n\n</body>"
    
    # Fix image wrapped in <p></p>
    bad_image = '<p><img src="../Images/gem.gif" alt="Spinning Black Gem" width="120" height="67.5" /></p>'
    if bad_image in html:
        log.info("Found misformated image in Chapter " + chapter + ". Reformatted HTML.")
        good_image = '<img src="../Images/gem.gif" alt="Spinning Black Gem" width="120" height="67.5" />'
        html = html.replace(bad_image, good_image)
        
    # Prettify the generated html
    soup = BeautifulSoup(html, features="html.parser")
    html = soup.prettify()
    
    # Save the updated html to Database
    doc.html = html
    doc.save()
    log.info("Updated Chapter " + chapter + " html field.")

def get_toc():
    toc = {}
    count = 0

    # Use bs4 to get bad words off chapter text
    URL = "https://bestlightnovel.com/novel_888112448"
    page = get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="list_chapter")
    links = results.find_all("a")

    # For every link in "list_chapter"
    for link in links:
        link_text = str(link.text)
        link_text = link_text.strip()
        chapter_number = int(re.findall(r'\d+', link_text)[0])
        chapter = str(chapter_number)

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
                title = link_text
        title = max_title(title) # End of Title

        # Chapter URL
        link_url = link["href"]

        # Save Path
        savePath = 'chapters/' + str(chapter) + '.md'

        # Fix Chapter 39.1
        if "Saint Paul (1)" in title:
            toc[39] = {"title": "Saint Paul - Part 1",
                        "url": link_url, "path": savePath}
        elif "Saint Paul (2)" in title:
            toc[40] = {"title": "Saint Paul - Part 2",
                        "url": link_url, "path": savePath}
        else:
            toc[chapter_number] = {"title": title,
                                    "url": link_url, "path": savePath}

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

def get_ch_head(title, chapter):
    chapter = str(chapter)
    html_head = '<?xml version="1.0" encoding="utf-8"?>\n'
    html_head += "<!DOCTYPE html>\n\n"
    html_head += '<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xmlns:epub="http://www.idpf.org/2007/ops">\n'
    html_head += "<head>\n"
    html_head += '  <meta charset="utf-8"/>\n'
    html_head += "  <title>" + title + "</title>\n"
    html_head += '  <meta name="chapter" content="' + chapter + '"/>\n'
    html_head += '  <link type="text/css" rel="stylesheet" href="../Styles/sg.css"/>\n'
    html_head += "</head>\n\n"
    html_head += "<body>\n\n"
    return html_head

def get_sec_head(title, section):
    section = str(section)
    html_head = '<?xml version="1.0" encoding="utf-8"?>\n'
    html_head += "<!DOCTYPE html>\n\n"
    html_head += '<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xmlns:epub="http://www.idpf.org/2007/ops">\n'
    html_head += "<head>\n"
    html_head += '  <meta charset="utf-8"/>\n'
    html_head += "  <title>" + title + "</title>\n"
    html_head += '  <meta name="section" content="' + section + '"/>\n'
    html_head += '  <link type="text/css" rel="stylesheet" href="../Styles/sg.css"/>\n'
    html_head += "</head>\n\n"
    html_head += "<body>\n\n"
    return html_head

def remove_editing_tag(tags):
    if "editing" in tags:
        tags.remove("editing")
    return tags
    
def clean_tags(): 
    lp("\nCleaning Tags\n\n")
    atlas()
    for doc in tqdm(Chapter.objects,unit="ch"):
        doc_tags = set((doc.tags))
        doc_tags = remove_editing_tag(doc_tags)
        length = len(doc_tags)
        if length > 0:
            tags = []
            for tag in doc_tags:
                tags.append(tag)
            doc.tags = tags
            doc.save()
        else:
            doc.tags = []
            doc.save()
            
def update_titles():
    with open ("JSON/toc.json", 'r') as infile:
        toc = dict((load(infile)))
    
    atlas()
    for doc in tqdm(Chapter.objects,unit="ch",desc="updating titles"):
        chapter = str(doc.chapter)
        title = toc[chapter]["title"]
        title = max_title(title)
        doc.title = title
        doc.save()

def write_chapters():
    
    atlas()
    for doc in tqdm(Chapter.objects, unit="ch", desc="writing chapters"):
        text = get_text(doc)
        chapter = str(doc.chapter)
        filename = chapter +".md"
        filepath = "chapters/" + filename
        with open (filepath, 'w')as outfile:
            outfile.write(text)
    lp("Wrote all chapters to disk")
    
    
# Main()
def update_db():
    # Get URIs from authkey.json and register them
    with open ("JSON/authkey.json", "r") as json:
        authkey = dict((load(json)))
    supergene = authkey["supergene"]
    sg = authkey["sg"]
    register_connection(alias="supergene", host=supergene)
    register_connection(alias="sg", host=sg)

    with open (TOC_PATH, 'r') as infile:
        toc = dict((load(infile)))
    keys = toc.keys()
    chapters = []
    for key in keys:
        chapter = int(key)
        chapters.append(chapter)

    connect(db="supergene",host=supergene)
    class Chapter(Document):
        chapter = IntField(Required=True, unique=True)
        title = StringField(Required=True, max_length=200)
        original_text = StringField(Required=True)
        text = StringField()
        final_text = StringField()
        url = URLField(Required=True)
        css = StringField(max_length=200)
        tags = ListField(StringField(max_length=50), default=list)
        added = DateTimeField(default=datetime.now)
        image = StringField(max_length=200)
        head = StringField(max_length=800)
        section = IntField()
        book = IntField()
        atx = StringField(max_length=500)
        html = StringField()
        edited = BooleanField()
    dictionary = {}
    for ch in tqdm(chapters, unit="ch", desc="Writing to Dictionary"):
        for doc in Chapter.objects(chapter=ch):
            chapter_doc = {
                "chapter": doc.chapter,
                "title": doc.title,
                "text": get_text(doc),
                "section": doc.section,
                "book": doc.book,
                "tags": doc.tags
            }
            dictionary[str(doc.chapter)] = chapter_doc  
    
    with open ("JSON/chapter-out.json", 'w') as outfile:
        dump(dictionary, outfile, indent=4)
    lp("wrote chapter data to JSON")
    disconnect_all()
    

def new_db():
    with open ("JSON/authkey.json", "r") as json:
        authkey = dict((load(json)))
        
    supergene = authkey["supergene"]
    sg = authkey["sg"]
    register_connection(alias="supergene", host=supergene)
    register_connection(alias="sg", host=sg)
    try:
        connect("sg", host=sg)
        lp("Connected to Databas SG.")
    except:
        lp("Unable to connect to " + sg)
        
    with open ("JSON/chapter-out.json", 'r') as infile:
        chapters = dict((load(infile)))
        
    keys = chapters.keys()
    class Book(Document):
        book = IntField(primary_key=True)
        title = StringField(Required=True, max_length=500)
        output = StringField()
        cover = StringField()
        cover_path = StringField()
        uuid = StringField()
        default = StringField()
        start = IntField()
        end = IntField()   
        
    class Section(Document):
        section = IntField(primary_key=True)
        title = StringField(Required=True, max_length=250)
        body = StringField()
        book = LazyReferenceField(Book)
        
    class Chapter(Document):
        chapter = IntField(primary_key=True)
        title = StringField(max_length=200, Required=True)
        text = StringField()
        html = StringField()
        tags = ListField(StringField(max_length=50))
        section = LazyReferenceField(Section)
        book = LazyReferenceField(Book)
        created = DateTimeField(default=datetime.now())
        modified = DateTimeField(default=datetime.now())
        
        
    for key in tqdm(keys, unit="ch", desc="Writing new documents"):
        ch_dict = chapters[key]
        
    
def make_book_db():
    
    with open ("JSON/authkey.json", 'r') as json:
        auth = dict((load(json)))
    sg = auth["sg"]
    
    connect("sg",host=sg)
    
    class Book(Document):
        _id = IntField(primary_key=True)
        book = IntField(Required=True, unique=True)
        title = StringField(Required=True, max_length=500)
        output = StringField()
        cover = StringField()
        cover_path = StringField()
        uuid = StringField()
        default = StringField()
        start = IntField()
        end = IntField()   
    
    with open("JSON/drafts.json", 'r') as infile:
        json = dict((load(infile)))
        
    keys = json.keys()
    for key in keys:
        dic = json[key]
        new_book = Book(
            book = int(key),
            title = max_title(dic["title"]),
            output = dic["output"],
            cover = dic["cover"],
            cover_path = dic["cover_path"],
            uuid = dic["uuid"],
            default = "",
            start = dic["ch_start"],
            end = dic["ch_end"]
        )
        new_book.save()
        
def make_section_db():
    
    with open ("JSON/authkey.json", 'r') as json:
        auth = dict((load(json)))
    sg = auth["sg"]
    
    connect("sg",host=sg)
    
    class Section(Document):
        _id = IntField(primary_key=True)
        section = IntField(Required=True, unique=True)
        title = StringField(Required=True, max_length=250)
        html = StringField()
        start = IntField()
        end = IntField()
        book = LazyReferenceField(Book)
        
    with open ("JSON/section.json", 'r') as infile:
        sections = load(infile)
    for sec in sections:
        sect = int(sec["section"])
        if sect != 0:
            new_section = Section(
                _id = sect,
                section = sect,
                title = max_title(sec["title"]),
                html = "",
                start = int(sec["ch_start"]),
                end = int(sec["ch_end"]),
                book = int(sec["book"])
            )
        else:
            new_section = Section (
                _id = sect,
                section = sect,
                title = max_title(sec["title"]),
                html = "",
                book = int(sec["book"])
            )    
        new_section.save()
        
make_section_db()