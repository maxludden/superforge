# Create Book

from ctypes import DEFAULT_MODE
from mongoengine import connect
from tqdm.auto import tqdm
from uuid import uuid4 as uuid
from main import Chapter, Section, lp, connect_atlas, con_atlas
from SG import get_ch_head, get_sec_head
from shutil import copy
from markdown2 import markdown as md
from json import load, dump
import re
import os

# Declare Constants
MAIN_DIR = ''
DRAFTS = 'Drafts/'
COVER1 = 'Draft Docs/Images/cover1.png'
COVER2 = 'Draft Docs/Images/cover2.png'
COVER3 = 'Draft Docs/Images/cover3.png'
COVER4 = 'Draft Docs/Images/cover4.png'
COVER5 = 'Draft Docs/Images/cover5.png'
COVER6 = 'Draft Docs/Images/cover6.png'
COVER7 = "Draft Docs/Images/cover7.png"
COVER8 = "Draft Docs/Images/cover8.png"
COVER9 = "Draft Docs/Images/cover9.png"
GEM = 'Draft Docs/Images/gem.gif'
SGCSS = 'Draft Docs/Styles/sg.css'
LEMON = 'Draft Docs/Styles/Lemon Milk Pro Regular.otf'
DRAFT_DICT = "JSON/drafts.json"
SECTION_DICT = "JSON/section.json"
CHAPTER_INDEX = 'JSON/chapter_index.json'
LOG_PATH = 'logs/book.log'
META = 'Draft Docs/Meta/meta.yaml'
EPUB_META = 'Draft Docs/Meta/epub-meta.yaml'

def make_dirs(book):
    # Make Draft Directoroes
    book_dir = str("book-" + str(book))
    parent_dir = 'Drafts'
    path = os.path.join(parent_dir, book_dir)
    os.makedirs(path)
    
    # HTML
    html_dir = "html"
    html_path = os.path.join(path, html_dir)
    os.makedirs(html_path)

    # Images
    images_dir = "Images"
    image_path = os.path.join(path, images_dir)
    os.makedirs(image_path)


    paths = {
        'book': path,
        'html': html_path,
        'img': image_path,
    }
    return paths

def make_default_doc(book):
    book = int(book)
    with open(DRAFT_DICT, 'r') as infile:
        book_json = load(infile)
    book_data = book_json[book]
    
    with open("JSON/book_sec.json", 'r')as infile:
        book_sections = dict((load(infile)))

    # Connect to supergeneDB
    connect_atlas()

    last_draft = book_data['draft']
    draft_num = last_draft + 1
    book_data['draft'] = draft_num
    book_json[book] = book_data
    with open(DRAFT_DICT, 'w') as outfile:
       dump(book_json, outfile, indent=4)
    title = book_data[str(book)]["title"]

    # Make Directories
    paths = make_dirs(book)
    path = paths['book']
    html_path = paths['html']
    img_path = paths['img']

    # Get Book Index
    with open(CHAPTER_INDEX, 'r') as infile:
        index = load(infile)
    key = str(book)
    book_index = index[key]

    # Copy Files
    covers = {
        1: COVER1,
        2: COVER2,
        3: COVER3,
        4: COVER4,
        5: COVER5,
        6: COVER6,
        7: COVER7,
        8: COVER8,
        9: COVER9
    }
    cover = covers[book]
    images = [cover, GEM]
    for image in images:
        copy(image, img_path)
        copy(image, html_path)
    copy(SGCSS, html_path)
    copy(LEMON, html_path)
    
    # Write metadata files
    meta = "---\ntitle: " + title + "\nauthor: Twelve Winged Dark Seraphim\n..."
    with open("Drafts/book" + str(book) + "/html/meta.yaml", 'w') as outfile:
        outfile.write(meta)
    with open("Draft Docs/epub-meta.yaml") as infile:
        epub_meta = infile.read()
    epub_meta = epub_meta.replace('TITLE',title)
    epub_meta = epub_meta.replace("COVER", "cover" + str(book))
    with open("Drafts/book" + str(book) + "/html/epub-meta.yaml", 'w') as outfile:
        outfile.write(epub_meta)

    # Make Index and resource strings
    with open(DRAFT_DICT, "r") as infile:
        draftDic = load(infile)
    output_file = draftDic[str(book)]['output']
      
   
    index = '---\nfrom: html\nto: epub3\n\noutput-file: ' + output_file + '\n\ninput-files:\n'
    new_cover = cover.replace('Draft Docs', path)
    new_cover = new_cover.replace('Images','html')
    new_gem = GEM.replace('Draft Docs',path)
    new_gem = new_gem.replace('Images','html')
    new_css = SGCSS.replace('Draft Docs', path)
    new_css = new_css.replace('Styles','html')
    resource_index = '- .\n- ' + new_cover +'\n- ' + new_gem +'\n- ' + new_css + '\n'
    

    # Populate strings & write MMD
    for line in tqdm(book_index, ncols=100, unit='ch', desc="Book " + str(book)):
        if line == 'titlepage':
            '''Title Page'''
            for doc in Section.objects(section=0):
                filename = doc.filename
                wfilepath = path + '/MMD/' + filename + '.md'
                add_to_index = '- ' + filename + '.html\n'
                index += add_to_index
                resource = '- ' + path + '/HTML/' + filename + '.html\n'
                resource_index += resource
                with open(wfilepath, 'w') as outfile:
                    outfile.write(doc.body)
            
        elif 'section-0' in line:
            '''Section Page''' 
            result = re.search(r'\d+', line)
            match = int(result.group())
            for doc in Section.objects(section=match):
                filename = doc.filename
                wfilepath = html_path+ "/" + filename + '.html'
                add_to_index = '- ' + filename + '.html\n'
                index += add_to_index
                resource = '- ' + html_path + "/" + filename + '.html\n'
                resource_index += resource
                section_head = get_sec_head(match)
                body = md(doc.body)
                html = section_head + body + "\n\n</body>"
                with open(wfilepath, 'w') as outfile:
                    outfile.write(html)
        else:
            '''Chapter'''
            result = re.search(r'\d+', line)
            match = int(result.group())
            for doc in Chapter.objects(chapter=match):
                # Get filepaths
                chapter = str(doc.chapter)
                filename = 'chapter-' + chapter.zfill(5)
                wfilepath = html_path + "/" + filename + '.html'
                add_to_index = '- ' + filename + '.html\n'
                index += add_to_index
                resource = '- ' + path + '/html/' + filename + '.html\n'
                resource_index += resource
                with open(wfilepath, 'w') as outfile:
                    outfile.write(doc.html)
    
    cover_filenames = {
        1: "cover1.png",
        2: "cover2.png",
        3: "cover3.png",
        4: "cover4.png",
        5: "cover5.png",
        6: "cover6.png",
        7: "cover7.png",
        8: "cover8.png",
        9: "cover9.png"
    }
    cover_filename = cover_filenames[book]

    '''Create Default Doc'''
    default_doc = index + '\nstandalone: true\nself-contained: true\n\nresource-path:\n'
    default_doc = default_doc + resource_index + '- ' + html_path + '/Lemon Milk Pro Refular.otf\n'
    default_doc = default_doc + '- ' + html_path + '/epub-meta.yaml\n- ' + html_path + '/meta.yaml\n'
    default_doc = default_doc + '\ntoc: true\ntoc-depth: 3\n\nepub-chapter-level: 3\n'
    default_doc = default_doc + 'epub-cover-image: ' + cover_filename + '\n'
    default_doc = default_doc + 'epub-fonts:\n- Lemon Milk Pro Regular.otf\n\n'
    default_doc = default_doc + 'epub-metadata: epub-meta.yaml\n\nmetadata-files:\n'
    default_doc = default_doc + '- epub-meta.yaml\n- meta.yaml\n\n'
    default_doc = default_doc + 'css:\n- sg.css\n...'
 
    default_doc_path = html_path + '/sg.yaml'
    with open (default_doc_path, 'w') as outfile:
        outfile.write(default_doc)


    finished_msg1 = "Completed Book " + str(book) + " - Draft " + str(draft_num) + '.'
    finished_msg2 = "Please try to render the book now."
    print (finished_msg1)
    print (finished_msg2)
   
def add_section_ch():  
    # Open json dictionaries.
    with open(SECTION_DICT, 'r') as sjson:
        section_dict = dict((load(sjson)))
    with open(DRAFT_DICT, 'r') as djson:
        draft_dict = dict((load(djson)))
    with open("JSON/skipped_ch.json", 'r') as skip:
        skipped = set((load(skip)))

    connect_atlas()
    keys = section_dict.keys()
    for key in keys:
        lp("Working on Section " + str(key))
        section = str(key)
        section_num = int(section)
        if section_num != 0:
            start = int(section_dict[key]["ch_start"])
            end = int(section_dict[key]["ch_end"]) + 1
            length = end - start
            ch_range = range(length)
            chapter_list = []
            for ch1 in ch_range:
                ch_num = start + ch1
                if ch_num != 3095 | ch_num != 3117:
                    chapter_list.append(ch_num)
            section_dict[key]["chapters"] = chapter_list

    with open(SECTION_DICT, 'w') as sjson:
        dump(section_dict, sjson, indent=4, sort_keys=True)
        
def make(book, write_html):
    book = str(book)
    book_num = int(book)
    
    
    # make paths
    book_path = "Drafts/book" + book
    html_path = book_path + "/html/"
    img_path = book_path + "/Images/"
    paths = [book_path, html_path, img_path]
    lp("Created or Verified Directories")
    for path in paths:
        try:
            os.makedirs(path, exist_ok=True)
        except:
            print("Unable to make path:\n\t" + path)
            
    # Copy Files
    covers = {
        1: COVER1,
        2: COVER2,
        3: COVER3,
        4: COVER4,
        5: COVER5,
        6: COVER6,
        7: COVER7,
        8: COVER8,
        9: COVER9
    }
    cover = covers[book_num]
    images = [cover, GEM]
    img_resource_paths = "\n- " + html_path + "cover" + book + ".png"
    img_resource_paths += "\n- " + img_path + "cover" + book + ".png"
    img_resource_paths += "\n- " + html_path + "gem.gif"
    img_resource_paths += "\n- " + img_path + "gem.gif"
    for image in images:
        copy(image, img_path)
        lp("Copied " + image + " to Image Directory")
        copy(image, html_path)
        lp("Copied " + image + " to HTML Directory")
    copy(SGCSS, html_path)
    lp("Copied sg.css to HTML Directory")
    copy(LEMON, html_path)
    lp("Copied Lemon/Milk Font to HTML Directory")
    
    with open(DRAFT_DICT, 'r') as infile:
        drafts = dict((load(infile)))
    title = drafts[book]["title"]
    output = drafts[book]["output"]
    cover_filename = drafts[book]["cover"]
    
    # Write Metadata Files
    meta = "---\ntitle: " + title + "\nauthor: Twelve Winged Dark Seraphim\n..."
    with open("Drafts/book" + str(book) + "/html/meta.yaml", 'w') as outfile:
        outfile.write(meta)
    lp("Wrote epub.yaml to HTML Directory")
    with open("Draft Docs/epub-meta.yaml", 'r') as infile:
        epub_meta = infile.read()
    epub_meta = epub_meta.replace('TITLE',title)
    epub_meta = epub_meta.replace("COVER", "cover" + str(book))
    with open("Drafts/book" + str(book) + "/html/epub-meta.yaml", 'w') as outfile:
        outfile.write(epub_meta)
    lp("Wrote epub-meta.yaml to HTML Directory")
            
    input_files = ""
    resource_paths = ""
    
    # Get book index from chapter idex
    with open(CHAPTER_INDEX, 'r') as infile:
        index = dict((load(infile)))
    book_index = index[book]
    
    # Write Sections and Chapters to directory and add them to default doc
    connect_atlas()
    for item in tqdm(book_index,desc="Creating Book " + book):
        if write_html == True:
            if item == "titlepage":
                '''Titlepage'''
                input_files += "- titlepage.html\n"
                con_atlas()
                for doc in Section.objects(section=0):
                    body = doc.body
                    title = doc.title
                    filename = doc.filename
                head = get_sec_head(title,0)
                body = md(body)
                html = head + body + "\n\n</body"
                filepath = html_path + filename + ".html"
                resource_paths += "- " + filepath
                if write_html == True:
                    with open (filepath, 'w') as outfile:
                        outfile.write(html)
                    lp("Wrote Titlepage to HTML Directory")
                con_atlas()
            elif "section-" in item:
                '''Section Page'''
                input_files += "\n- " + item + ".html"
                section = int(item.replace("section-", ""))
                con_atlas()
                for doc in Section.objects(section=section):
                    title = doc.title
                    body = doc.body
                    filename = doc.filename
                head = get_sec_head(title,section)
                body = md(body)
                html = head + body + "\n\n</body>"
                filepath = html_path + filename + ".html"
                resource_paths += "\n- " + filepath
                if write_html == True:
                    with open (filepath, 'w') as outfile:
                        outfile.write(html)
                    lp("Wrote Section " + str(section) + " to HTML Directory")
                con_atlas()
            else:
                '''Chapter'''
                input_files += "\n- " + item + ".html"
                chapter = int(item.replace("chapter-", ""))
                for doc in Chapter.objects(chapter=chapter):
                    html = doc.html
                filename = item + ".html"
                filepath = html_path + filename
                resource_paths += "\n- " + filepath
                if write_html == True:
                    with open(filepath, 'w') as outfile:
                        outfile.write(html)
                    lp("Wrote Chapter " + str(chapter) + " to HTML Directory")
        else:
            if item == "titlepage":
                input_files = "- titlepage.html"
                resource_paths = "- " + html_path + "titlepage.html"
            elif "section-" in item:
                input_files += "\n- " + item + ".html"
                resource_paths += "\n- " + html_path + item + ".html"
            else:
                input_files += "\n- " + item + ".html"
                resource_paths += "\n- " + html_path + item + ".html"
    default_doc = '---\nfrom: html\nto: epub3\n\noutput-file: ' + output + '\n\ninput-files:\n'        
    default_doc = default_doc + input_files
    default_doc = default_doc + '\n\nstandalone: true\nself-contained: true\n\nresource-path:\n'
    default_doc = default_doc + resource_paths + '\n- ' + html_path + 'Lemon Milk Pro Regular.otf'
    default_doc = default_doc + '\n- ' + html_path + 'epub-meta.yaml\n- ' + html_path + 'meta.yaml'
    default_doc = default_doc + img_resource_paths
    default_doc = default_doc + '\n\ntoc: true\ntoc-depth: 3\n\nepub-chapter-level: 3\n'
    default_doc = default_doc + 'epub-cover-image: ' + cover_filename + '\n'
    default_doc = default_doc + 'epub-fonts:\n- Lemon Milk Pro Regular.otf\n\n'
    default_doc = default_doc + 'epub-metadata: epub-meta.yaml\n\nmetadata-files:\n'
    default_doc = default_doc + '- epub-meta.yaml\n- meta.yaml\n\n'
    default_doc = default_doc + 'css:\n- sg.css\n...'
 
    default_doc_path = html_path + 'sg.yaml'
    with open (default_doc_path, 'w') as outfile:
        outfile.write(default_doc)

def update_chapters(doc):
    pass
