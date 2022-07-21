# Super Gene mongoDB

from json import load
from datetime import datetime
from tqdm.auto import tqdm
from main import Chapter, Section, atlas
from SG import db_parse_chapter

TOC_PATH = "JSON/toc.json"


atlas()

with open(TOC_PATH, 'r') as infile:
    toc = load(infile)

added = 34
chapters = []
keys = toc.keys()
for key in keys:
    chapterNum = int(key)
    if chapterNum > added:
        chapter = str(chapterNum)
        chapters.append(chapter)

for chapter in tqdm(chapters,ncols=110,unit='ch'):
    # Get chapter path from ToC and read file.
    chapterPath = str(toc[chapter]['path'])
    with open(chapterPath, 'r') as infile:
        original_text = infile.read()
    original_text = str(original_text)
    # Get Title, Chapter Number, and URL
    title = str(toc[chapter]['title']).title()
    chapterNum = int(chapter)
    chapter_url = toc[chapter]['url']
    # Generate Markdown Head
    meta = str("Title:" + title + "\nChapter:" + chapter + "\nCSS:../Styles/sg.css\n\n")
    atx = "### " + title + "\n#### Chapter " + chapter + "\n\n"
    mdImage = "![](../Images/gem.gif)\n\n"
    mdHead = str(meta + atx + mdImage)
    
    # Generate Chapter Document
    new_chapter = Chapter(
        chapter = chapterNum,
        title = title,
        original_text = original_text,
        text = "",
        url = chapter_url,
        markdown_meta = meta,
        atx = atx,
        image = mdImage,
        head = mdHead
    )
    
    new_chapter.save()
    new_chapter = db_parse_chapter(new_chapter)
    new_chapter.save()
