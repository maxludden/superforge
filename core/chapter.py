# core/chapter.py

import os
import re
import sys
from fileinput import filename
from platform import platform
from subprocess import run
from typing import Callable, Optional
from json import dump, load
from multiprocessing import Pool, Queue, Process
from functools import partial
from itertools import chain

from icecream import ic
from mongoengine import Document
from mongoengine.fields import EnumField, IntField, StringField
from pymongo import MongoClient
from tqdm.auto import tqdm, trange
from alive_progress import alive_bar
from dotenv import load_dotenv

from core.atlas import max_title, sg, mconnect
from core.log import errwrap, log


# .┌─────────────────────────────────────────────────────────────────┐.#
# .│                           Chapter                               │.#
# .└─────────────────────────────────────────────────────────────────┘.#
#
load_dotenv()
URI = os.getenv("SUPERGENE")


class ChapterNotFound(Exception):
    pass


class Chapter(Document):
    chapter = IntField(required=True, unique=True)
    section = IntField()
    book = IntField(min_value=1, max_value=10, required=True)
    title = StringField(max_length=500, required=True)
    text = StringField()
    filename = StringField()
    md_path = StringField()
    html_path = StringField()
    md = StringField()
    html = StringField()
    
    def __repr__(self):
        yaml_doc = f"---\nChapter: {self.chapter}\nSection: {self.section}\nBook {self.book}\nTitle: {self.title}\nFilename: {self.filename}\nMD Path: {self.md_path}\nHTML Path: {self.html_path}\n..."
        md = "\n# Chapter {self.chapter} Markdown\n  \n{self.md}"
        text = f"Text:\n  \n{self.text}\n"
        html = f"HTML:\n  \n{self.html}"
        return yaml_doc + md + text + html
        


@errwrap()
def generate_section(chapter: int):
    """
    Determines the given chapter's section.

    Args:
        `chapter` (int):
            The given chapter.

    Raises:
        `ValueError`: Invalid Chapter Number

    Returns:
        `section` (int):
            The section that the given chapter belongs to.
    """
    log.debug(f"Called generate_section(chapter={chapter})")
    if chapter <= 424:
        return 1
    elif chapter <= 882:
        return 2
    elif chapter <= 1338:
        return 3
    elif chapter <= 1679:
        return 4
    elif chapter <= 1711:
        return 5
    elif chapter <= 1821:
        return 6
    elif chapter <= 1960:
        return 7
    elif chapter <= 2165:
        return 8
    elif chapter <= 2204:
        return 9
    elif chapter <= 2299:
        return 10
    elif chapter <= 2443:
        return 11
    elif chapter <= 2639:
        return 12
    elif chapter <= 2765:
        return 13
    elif chapter <= 2891:
        return 14
    elif chapter <= 3033:
        if chapter == 3095:
            log.warning(f"Chapter {chapter} was inputted to generate_section().\nChapter {chapter} does not exist.")
        elif chapter == 3117:
            log.warning(f"Chapter {chapter} was inputted to generate_section(). \nChapter {chapter} does not exist.")
            pass
        else:
            return 15
    elif chapter <= 3303:
        return 16
    elif chapter <= 3462:
        return 17
    else:
        raise ValueError("Invalid Chapter", f"\nChapter: {chapter}")


@errwrap()
def get_section(chapter: int):
    """
    Retrieve the section of a given chapter from MongoDB.

    Args:
        `chapter` (int):
            The given chapter.

    Raises:
        ValueError: Invalid Chapter number

    Returns:
        `section` (int):
            The section of the given chapter.
    """
    sg()
    for doc in Chapter.objects(chapter=chapter):
        return doc.section


@errwrap()
def generate_book(chapter: int):
    """
    Generate the book for a given chapter.

    Args:
        `chapter` (int):
            The given chapter.

    Raises:
        `ValueError`: Invalid Section Number

    Returns:
        `book` (int):
            The book of the given chapter
    """

    section = generate_section(chapter)
    log.debug(f"Section: {section}")
    if section == 1:
        return 1
    elif section == 2:
        return 2
    elif section == 3:
        return 3
    elif section == 4 | section == 5:
        return 4
    elif section == 6 | section == 7:
        return 5
    elif section == 8 | section == 9:
        return 6
    elif section == 10 | section == 11:
        return 7
    elif section == 12 | section == 13:
        return 8
    elif section == 14 | section == 15:
        return 9
    elif section == 16 | section == 17:
        return 10
    else:
        raise ValueError("Invalid Section Input.", f"Section: {section}")


@errwrap()
def get_book(chapter: int):
    """
    Retrieve the book for the given chapter from MongoDB.

    Args:
        `chapter` (int):
            The given chapter.

    Returns:
        `book` (int):
            The book for the given chapter.
    """
    sg()
    for doc in Chapter.objects(chapter=chapter):
        return doc.book


@errwrap()
def get_title(chapter: int):
    """
    Retrieve the Title of the given chapter from MongoDB.

    Args:
        `chapter` (int):
            The given chapter.

    Returns:
        `title` (str):
            The title of the given chapter.
    """
    sg()
    for doc in Chapter.objects(chapter=chapter):
        title = max_title(doc.title)
        return title


@errwrap()
def generate_filename(chapter: int):
    """
    Generate the filename for the given chapter.

    Args:
        `chapter` (int):
            The given chapter.

    Returns:
        `filename` (str):
            the filename (without extension) for the given chapter.
    """
    chapter_str = str(chapter).zfill(4)
    return f"chapter-{chapter_str}"


@errwrap()
def get_filename(chapter: int):
    """
    Retrieve the filename of the given chapter from MongoDB.

    Args:
        `chapter` (int):
            The given chapter.

    Returns:
        `filename` (str):
            The filename of the given chapter without a file extension.
    """
    sg()
    for doc in Chapter.objects(chapter=chapter):
        return doc.filename


@errwrap()
def generate_md_path(chapter: int):
    """
    Generates the path to where the given chapter's multimarkdown will be stored.

    Args:
        `chapter` (int)
            The given chapter.

    Returns:
        `md_path` (str):
            The filepath of the the given chapter's multimarkdown.
    """
    # > Generate book and filename from the given chapter
    book = generate_book(chapter)
    filename = generate_filename(chapter)

    # > Pad the chapter number to four digits
    book_dir = str(book).zfill(2)

    # > Platform OS
    if platform() == "Linux":
        ROOT = "home"  # < WSL2
    else:
        ROOT = "Users"  # < Max

    BASE = f"/{ROOT}/maxludden/dev/py/superforge/"
    md_path = f"{BASE}/books/book{book_dir}/md/{filename}.md"
    return md_path


@errwrap()
def get_md_path(chapter: int):
    """
    Retrieve the path of the the given chapter's multimarkdown from MongoDB.

    Args:
        `chapter` (int):
            The given chapter.

    Returns:
        `md_path` (str):
            The filepath for the given chapter.
    """
    sg()
    for doc in Chapter.objects(chapter=chapter):
        return doc.md_path


@errwrap()
def generate_html_path(chapter: int):
    """
    Generates the path to where the given chapter's HTML will be stored.

    Args:
        `chapter` (int)
            The given chapter.

    Returns:
        `html_path` (str):
            The filepath to the given chapter's HTML.
    """
    book = generate_book(chapter)
    filename = generate_filename(chapter)

    book_dir = str(book).zfill(2)

    # > Platform OS
    if platform() == "Linux":
        ROOT = "home"  # < WSL2
    else:
        ROOT = "Users"  # < Max

    BASE = f"/{ROOT}/maxludden/dev/py/superforge/"
    html_path = f"{BASE}/books/book{book_dir}/html/{filename}.html"
    return html_path


@errwrap()
def get_html_path(chapter: int):
    """
    Retrieve the filepath of the given chapter from MongoDB.

    Args:
        `chapter` (int):
            The given chapter.

    Returns:
        `html_path` (str):
            The filepath of the given chapter.
    """
    sg()
    for doc in Chapter.objects(chapter=chapter):
        return doc.html_path


@errwrap(entry=False, exit=False)
def generate_md(chapter: int, save: bool = False, write: bool = False) -> str:
    """
    Generates the multimarkdown string for the given chapter. Saves the markdown string to disk (md_path) as well as to MongoDB.

    Requires an active connection to MongoDB.

    Args:
        `chapter` (int):
            The given chapter.

    Returns:
        `md` (str):
            The multimarkdown for the given chapter.
    """
    sg()
    for doc in Chapter.objects(chapter=chapter):
        # Books 4-10 have two sections a piece
        title = max_title(doc.title)
        # > Multimarkdown Metadata
        meta = f"Title:{title} \nChapter:{doc.chapter} \nSection:{doc.section} \nBook:{doc.book} \nCSS:../Styles/style.css \nviewport: width=device-width\n  \n"

        # > ATX Headers
        img = """<figure>\n\t<img src="../Images/gem.gif" alt="gem" id="gem" width="120" height="60" />\n</figure>\n  \n"""

        atx = f"## {title}\n### Chapter {doc.chapter}\n  \n{img}\n  \n  "

        # > Chapter Text
        text = f"{doc.text}\n"

        # > Concatenate Multimarkdown
        md = f"{meta}{atx}{text}"

        if save:
            doc.md = md
            doc.save()

        if write:
            with open(doc.md_path, "w") as outfile:
                outfile.write(md)
                log.debug("Wrote Chapter {doc.chapter}'s multimarkdown to disk.")
        return md


@errwrap(exit=False)
def get_md(chapter: int):
    """
    Retrieve the multimarkdown for the given chapter from MongoDB.

    Args:
        `chapter` (int):
            The given chapter.

    Returns:
        `md` (str):
            The multimarkdown of the given chapter.
    """
    sg()
    for doc in Chapter.objects(chapter=chapter):
        return doc.md


@errwrap(entry=False, exit=False)
def generate_html(chapter: int, save: bool = False) -> str:
    """
    Generate the HTML for a given chapter. Save the given chapter's HTML to disk (html_path) as well as to MongoDB.

    Args:
        `chapter` (int):
            The MongoDB Chapter document for the given chapter.

    Returns:
        `html` (str):
            The HTML for the given chapter.
    """
    sg()
    for doc in Chapter.objects(chapter=chapter):
        md_cmd = [
            "multimarkdown",
            "-f",
            "--nolabels",
            "-o",
            f"{doc.html_path}",
            f"{doc.md_path}",
        ]
        log.debug(f"Markdown Path: {doc.md_path}")
        log.debug(f"HTML Path: {doc.html_path}")
        log.debug(f"Multitmarkdown Command: &quot; &quot;.join({md_cmd})")
        try:
            result = run(md_cmd)

        except OSError as ose:
            raise OSError(ose)

        except ValueError as ve:
            raise ValueError(ve)

        except Exception as e:
            log.error(e)
            sys.exit(
                "Error occured in the proccess of creating HTML for Chapter {doc.chapter}"
            )

        else:
            log.debug(f"Result of MD Command: {result.__str__}")

        if save:
            with open(doc.html_path, "r") as chapter:
                html = chapter.read()
            log.debug(f"Saved Chapter {chapter}'s HTML to disk.")

            doc.html = html
            doc.save()
            log.debug(f"Saved Chapter {chapter}'s HTML to MongoDB.")
            return html


@errwrap(exit=False)
def get_html(chapter: int):
    """
    Retrieve the HTML of the given chapter from MongoDB.

    Args:
        `chapter` (int):
            The given chapter.

    Returns:
        `html` (str):
            The HTML of the given chapter.
    """
    sg()
    for doc in Chapter.objects(chapter=chapter):
        return doc.html


@errwrap()
def write_md(chapter: int):
    """
    Retrieves the given chapter's multimarkdown from MongoDB and writes it to disk (md_path)

    Args:
        `chapter` (int):
            The given chapter
    """
    sg()
    for doc in Chapter.objects(chapter=chapter):
        log.debug(f"MD Path: {doc.md_path}")
        length = len(doc.md)
        log.debug(f"Markdown Length: {length}")

        with open(doc.md_path, "w") as outfile:
            outfile.write(doc.md)
    log.debug(f"Wrote Chapter {chapter}'s Multimarkdown to Disk.")


@errwrap()
def make_chapters():
    """
    Generate the values needed to create the chapter.
    """
    sg()
    for doc in tqdm(Chapter.objects(), unit="ch", desc="Creating Chapters"):
        chapter = doc.chapter
        log.debug(f"Accessed Chapter {chapter}'s MongoDB Document.")

        # > Section
        section = generate_section(chapter)
        log.debug(f"Chapter {chapter}'s section: {section}")
        doc.section = section
        log.debug(f"Updated Chapter {chapter}'s {section}.")

        # > Book
        book = generate_book(chapter)
        log.debug(f"Chapter {chapter}'s book: {book}")
        doc.book = book
        log.debug(f"Updated Chapter {chapter}'s {book}.")

        # > Title
        title = get_title(chapter)
        log.debug(f"Chapter {chapter}'s title: {title}")
        doc.title = title
        log.debug(f"Updated Chapter {chapter}'s {title} in MongoDB.")

        # > Filename
        filename = generate_filename(chapter)
        log.debug(f"Chapter {chapter}'s Filename: {filename}")
        doc.filename = filename
        log.debug(f"Updated Chapter {chapter}'s filename in MongoDB")

        # > Md_path
        md_path = generate_md_path(chapter)
        log.debug(f"Chapter {chapter}'s Multitmarkdown Path: {md_path}")
        doc.md_path = md_path
        log.debug(f"Updated Chapter {chapter}'s Multimarkdown filepath.")

        # > Html_path
        html_path = generate_html_path(chapter)
        log.debug(f"Chapter {chapter}'s html_path: {html_path}")
        doc.html_path = html_path
        log.debug(f"Updated Chapter {chapter}'s {html_path}.")

        # #> Md
        # md = generate_md(chapter)
        # length = len(md)
        # log.debug(f"Chapter {chapter}'s md: {length}")
        # doc.md = md
        # log.debug(f"Updated Chapter {chapter}'s {md}.")

        # #> Html
        # html = generate_html(chapter)
        # length = len(html)
        # log.debug(f"Chapter {chapter}'s html length: {length}")
        # doc.html = html
        # log.debug(f"Updated Chapter {chapter}'s {html}.")

        doc.save()

        log.debug(f"Finished Chapter {chapter}.")


@errwrap()
def verify_chapters():
    """
    Update all the values of each chapter dict.
    """
    sg()
    for doc in tqdm(Chapter.objects(), unit="ch", desc="updating paths"):
        chapter = doc.chapter

        # > Section
        if doc.section != "":
            section = doc.section
        else:
            section = generate_section(chapter)
        doc.section = section
        log.debug(f"Section: {section}")

        # > Book
        if doc.book != "":
            book = doc.book
        else:
            book = generate_book(chapter)
        doc.book = book
        log.debug(f"Book: {book}")

        # > Md_path
        if doc.md_path != "":
            md_path = doc.md_path
        else:
            md_path = generate_md_path(chapter)
        doc.md_path = md_path
        log.debug(f"MD Path: {md_path}")

        # > HTML_path
        if doc.html_path != "":
            html_path = doc.html_path
        else:
            html_path = generate_html_path(chapter)
        doc.html_path = html_path
        log.debug(f"HTML Path: {html_path}")

        # > MD
        if doc.md != "":
            md = doc.md
        else:
            md = generate_md(chapter)
        doc.md = md
        length = len(md)
        log.debug(f"MD length: {length}")

        # > HTML
        if doc.html != "":
            html = doc.html
        else:
            html = generate_html(chapter)
        doc.html = html
        length = len(html)
        log.debug(f"HTML Length: {length}")

        doc.save()
        log.info(f"Finished chapter {chapter}")


@errwrap()
def write_book_md(book: int):
    sg()
    for doc in tqdm(Chapter.objects(book=book), unit="ch", desc=f"Book {book}"):
        with open(doc.md_path, "w") as outfile:
            outfile.write(doc.md)
        log.debug(f"Wrote CHapter {doc.chapter}'s Markdown to disk.")


@errwrap()
def write_book_html(book: int):
    sg()
    for doc in tqdm(Chapter.objects(book=book), unit="ch", desc=f"Book {book}"):
        with open(doc.html_path, "w") as outfile:
            outfile.write(doc.html)
            log.debug(f"Wrote CHapter {doc.chapter}'s HTML to disk.")


@errwrap()
def update_html_paths():
    sg()
    for doc in tqdm(Chapter.objects(), unit="ch", desc="Updating filepath"):
        base = f"Users/maxludden/dev/py/superforge/books/book"
        book_zfill = str(doc.book).zfill(2)
        filename = doc.filename
        filepath = f"{base}{book_zfill}/html/{filename}.html"
        print(filepath)
        doc.html_path = filepath
        doc.save()


@errwrap()
def replace_geno_core(match):
    """
    Replace the geno core with the correct version.
    """
    match_str = match.group(0)  # The entire match
    class_group = str(match.group("class")).capitalize()  # The class group
    core_group = max_title(str(match.group("core")))  # The core group

    replacement = f"""<div class="tables">
    <table class="center70">
        <tr>
            <th>{class_group} Geno Core</th>
        <tr></tr>
            <td>{core_group}</td>
        </tr>
    </table>
    <!--{match_str}-->
</div>"""
    return replacement


@errwrap()
def find(pattern: str | list[str]) -> list[str]:
    """
    Find all the matches of a pattern in Supergene.
    """
    if isinstance(pattern, str):
        pattern = [pattern]
    html = tqdm(Chapter.objects(), unit="ch", desc="")
    for p in pattern:
        html = re.sub(p, replace_geno_core, html)
    return html


@errwrap()
def edit(pattern: str, replacement: str | Callable) -> None:
    regex = re.compile(pattern)
    results = []
    sg()
    chapters = Chapter.objects.all()

    for doc in tqdm(chapters, unit="ch", desc="Editing"):
        # Read Chapter Data from MongoDB
        chapter = doc.chapter
        msg = f"Chapter {chapter}"

        # Search Chapter for Pattern
        text = doc.text
        matches = re.findall(regex, text)

        if len(matches) > 0:
            chapter_matches = {"chapter": chapter, "matches": len(matches)}
            for x, match in enumerate(matches, start=1):
                chapter_matches[f"match{x}"] = match
                if callable(replacement):
                    text = re.sub(pattern, replacement(match), text)
                else:
                    text = re.sub(pattern, replacement, text)

            results.append(chapter_matches)
            doc.text = text
            doc.save()
            msg = f"Chapter {chapter} - Saved Updated Chapter "
            log.debug(msg)
        else:
            msg = f"Chapter {chapter} - No Matches"
            log.debug(msg)
        log.debug(f"Finished chapter {doc.chapter}")
    return results


@errwrap()
def generate_text_path(chapter: int) -> str:
    """
    Generate the path to the text file for a chapter.
    """
    text_path = f"{BASE}/text/{chapter}.txt"
    return text_path


@errwrap()
def get_text(chapter: int) -> str:
    """
    Get the text of a chapter.
    """
    sg()
    doc = Chapter.objects(chapter=chapter).first()
    if doc is None:
        raise ChapterNotFound(f"Unable to find chapter {chapter}")
    text = doc.text
    return text


@errwrap()
def write_text(chapter: int) -> None:
    """
    Write the text of a chapter to a file.
    """
    sg()
    text = get_text(chapter)
    text_path = generate_text_path(chapter)
    with open(text_path, "w") as outfile:
        outfile.write(text)
    log.debug(f"Wrote CHapter {chapter}'s text to disk.")


@errwrap()
def write_texts() -> None:
    """
    Write the text of all chapters to disk.
    """
    sg()
    for chapter in tqdm(Chapter.objects(), unit="ch", desc="Writing Text"):
        write_text(chapter.chapter)
    log.info("Finished writing text.")


@errwrap()
def mget_text(chunk, input):
    """
    Retrieve the text of a given chapter.

    Args:
        chapter (int): The chapter to retrieve.

    Returns:
        text (str): The text of the chapter.
    """
    # > Connect to MongoDB
    URI = get_atlas_uri("SUPERGENE")
    client = client = MongoClient(URI, maxPoolSize=250)
    db = client.SUPERGENE
    chapters = db["chapter"]

    # > Loop over the _id's in the chunk and retrieve the text from each
    chunk_result_list = []
    for chapters in chunk:
        # > Get Chapter and it's text
        chapter = chapters.find_one({"chapter": chapter})
        text = chapter["text"]
        chunk_result_list.append({"chapter": chapter, "text": text})
    return chunk_result_list


@errwrap()
def make_text_dirs() -> None:
    for i in trange(1, 11, unit="ch", desc="Creating Text Directories"):
        book_str = str(i).zfill(2)
        path = os.path(f"BASE/books/book{book_str}/text")
        os.makedirs(path, exist_ok=True)
        log.debug(f"Created {path}")


@errwrap()
def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(1, 3463, n):
        if i == 3095 | i == 3117:
            continue
        else:
            yield l[i : i + n]


@errwrap()
def mget_text(chunk):
    """
    Retrieve the text of a given chapter.

    """
    # > Connect to MongoDB
    URI = get_atlas_uri("SUPERGENE")
    client = client = MongoClient(URI, maxPoolSize=250)
    db = client.SUPERGENE
    chapters = db["chapter"]

    # > Loop over the _id's in the chunk and retrieve the text from each
    chunk_result_list = []
    for chapter in chunk:

        # > Get Chapter and it's text
        chapter_doc = chapters.find_one({"chapter": chapter})
        text = chapter_doc["text"]
        chapter = chapter_doc["chapter"]
        text_path = generate_text_path(chapter)
        with open(text_path, "w") as outfile:
            outfile.write(text)
        chunk_result_list.append({"chapter": chapter, "text": text})


@errwrap()
def search(phrase: str, db: str = "SUPERGENE") -> int:
    """
    Search chapters for a phrase.

    Args:
        phrase (str): The phrase to search for.
        db (str): The database to search.

    Returns:
        chapters (int): The number of chapters containing the phrase.
    """
    # > Connect to SUPERGENE
    if db == "SUPERGENE":
        sg()
        for doc in tqdm(Chapter.objects(), unit="ch", desc="Searching"):
            text = doc.text
            if phrase in text:
                yield doc.chapter
