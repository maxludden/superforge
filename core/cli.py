# core/cli.py

import typer
from dotenv import load_dotenv
from mongoengine import connect

from core.atlas import sg, BASE
from core.log import log, errwrap
import core.chapter as chapter_

load_dotenv()

app = typer.Typer()

@app.command()
def get_chapter(chapter: int):
    sg()
    doc = chapter_.Chapter.objects(chapter=chapter).first()
    log.info(doc.__repr__())
    return doc