# utilities/fix_filepaths.py

import core.chapter as bk
import core.chapter as ch
import core.endofbook as eob
import core.epubmetadata as epubmd
import core.metadata as metad
import core.myaml as myaml
import core.section as sec
import core.titlepage as titlepage
from core.atlas import BASE, sg
from core.log import errwrap, log
from dotenv import load_dotenv
from tqdm.auto import tqdm

load_dotenv(".env")

# .┌─────────────────────────────────────────────────────────────────┐. #
# .│                        Fix Filepaths                            │. #
# .└─────────────────────────────────────────────────────────────────┘. #

@errwrap()
def chapter_generate_html_path(chapter: int, book: int):
    book_str = str(book).zfill(2)
    book_dir = f"book{book_str}"
    chapter_str = str(chapter).zfill(4)
    filename = f"chapter-{chapter_str}.html"
    log.debug(f"Chapter {chapter}'s Filename: {filename}")
    html_path = f"{BASE}/books/{book_dir}/html/{filename}"
    log.debug(f"Chapter {chapter}: {html_path}")
    return html_path


@errwrap()
def fix_chapter_html_paths():
    sg()
    chapter_position = 0
    for doc in tqdm(ch.Chapter.objects(), unit='ch', desc="Fixing Chapter Filepaths"):
        chapter_position += 1
        chapter = doc.chapter
        book = doc.book
        doc.html_path = chapter_generate_html_path(chapter, book)
        doc.save()
        
        msg = f"Updated Chapter {chapter}'s Filepath in MongoDB."
        if chapter_position % 50 == 0:
            log.info (msg)
        else:
            log.debug(msg)

@errwrap()
def chapter_generate_md_path(chapter: int, book: int):
    book_str = str(book).zfill(2)
    book_dir = f"book{book_str}"
    chapter_str = str(chapter).zfill(4)
    filename = f"chapter-{chapter_str}.md"
    log.debug(f"Chapter {chapter}'s Filename: {filename}")
    html_path = f"{BASE}/books/{book_dir}/md/{filename}"
    log.debug(f"Chapter {chapter}'s md_path: {html_path}")
    return html_path

@errwrap()
def fix_chapter_md_paths():
    sg()
    chapter_position = 0
    for doc in tqdm(ch.Chapter.objects(), unit='ch', desc="Fixing Chapter Filepaths"):
        chapter_position += 1
        chapter = doc.chapter
        book = doc.book
        doc.html_path = chapter_generate_md_path(chapter, book)
        doc.save()
        
        msg = f"Updated Chapter {chapter}'s Filepath in MongoDB."
        log.debug(msg)

#> Titlepage
@errwrap()
def generate_titlepage_md_path(book: int):
    book_str = str(book).zfill(2)
    book_dir = f"book{book_str}"
    newbase = f"{BASE}/books/{book_dir}"
    md_path = f"{newbase}/md/titlepage-{book_str}.md"
    return md_path

@errwrap()
def generate_titlepage_html_path(book: int):
    book_str = str(book).zfill(2)
    book_dir = f"book{book_str}"
    newbase = f"{BASE}/books/{book_dir}"
    html_path = f"{newbase}/html/titlepage-{book_str}.hmtl"
    return html_path
    
@errwrap()
def update_titlepage_paths():
    sg()
    for doc in tqdm(titlepage.Titlepage.objects(), unit="books"):
        doc.md_path = generate_titlepage_md_path(doc.book)
        doc.html_path = generate_titlepage_html_path(doc.book)
        doc.save()
        