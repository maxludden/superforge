# core/sort_json.py

import re
from json import dump, load

from tqdm.auto import tqdm

from core.atlas import max_title, sg
from core.chapter import Chapter
from core.log import errwrap, log


@errwrap()
def export_chapters():
    chapters = {}
    sg()
    for doc in tqdm(Chapter.objects(), unit="ch", desc="fixing chapters"):
        log.debug(f"Accessed Chapter {doc.chapter}'s document.")
        chapter = {
            "chapter": doc.chapter,
            "section": doc.section,
            "book": doc.book,
            "title": doc.title,
            "filename": doc.filename,
            "md_path": doc.mmd_path,
            "html_path": doc.html_path,
            "text": doc.text,
            "md": doc.mmd,
            "html": doc.html
        }
        chapters[doc.chapter]=chapter

    chapter_json = "/Users/maxludden/dev/py/superforge/json/chapter_export.json"
    with open(chapter_json, 'w') as outfile:
        dump({int(x):chapters[x] for x in chapters.keys()}, outfile, sort_keys=True, indent=4)
