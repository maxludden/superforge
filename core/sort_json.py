# core/sort_json.py

import re
from json import dump, load

from tqdm.auto import tqdm

from core.atlas import max_title, sg
from core.chapter import Chapter
from core.log import errwrap, log


@errwrap()
def export_chapters():
    
    chapter_json = f"{BASE}/json/chapter_export.json"
    response = input(f"Currently exporting to path:\n {chapter_json}\n\nIs that okay? (Y/N)")
    if response.lower() != 'y':
        chapter_json = input("Please enter the full path you would like to use:")
    
    chapters = {}
    sg()
    for doc in tqdm(Chapter.objects(), unit="ch", desc="fixing chapters"):
        log.debug(f"Accessed Chapter {doc.chapter}'s document.")
        md_path = doc.mmd_path.replace("supergene", "superforge").replace("/md/",'/md/').replace(".mmd",'.md')
        html_path = doc.html_path.replace('supergene', 'superforge')
        chapter = {
            "chapter": doc.chapter,
            "section": doc.section,
            "book": doc.book,
            "title": doc.title,
            "filename": doc.filename,
            "md_path": md_path,
            "html_path": html_path,
            "text": doc.text,
            "md": doc.mmd,
            "html": doc.html
        }
        chapters[doc.chapter]=chapter

    chapter_json = f"{BASE}/json/chapter_export.json"
    with open(chapter_json, 'w') as outfile:
        dump({int(x):chapters[x] for x in chapters.keys()}, outfile, sort_keys=True, indent=4)
