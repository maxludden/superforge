# core/defaultdoc.py
from yaml import load_all, SafeLoader, SafeDumper
from mongoengine import Document
from mongoengine.fields import IntField, StringField, ListField, DictField

from core.atlas import sg, max_title, ROOT
from core.log import log, errwrap
from core.book import Book
from typing import Optional

@errwrap()
def generate_output_file(book: int):
    '''
    Generate the output-file for the given book.

    Args:
        `book` (int):
            The given book.

    Returns:
        `output_file` (str): 
            The output-file for the given book.
    '''
    sg()
    for doc in Book.objects(book=book):
        return doc.output

@errwrap()
def generate_cover_image(book: int):
    '''
    Generate the filename for the given book's cover image.

    Args:
        `book` (int):
            The given book.

    Returns:
        `cover` (str): 
            The filename of the given books cover image.
    '''
    sg()
    for doc in Book.objects(book=book):
        return doc.cover

@errwrap()
def generate_epub_fonts():
    '''
    Generates a list of fonts to embed in the Ebook.

    Returns:
        `epub_fonts` (list[str]): 
            A list of fonts to embed in the Ebook.
    '''
    return [
        'Century Gothic.ttf',
        'abeatbykai.ttf',
        'Photograph Signature.ttf'
    ]

@errwrap()
def generate_meta(book: int):
    '''
    Generate the filename for the given book's metadata.

    Args:
        `book` (int):
            The given book

    Returns:
        `filename` (str): 
            The filename for the given book's metadata.
    '''
    return f"meta{book}.yaml"

@errwrap()
def generate_epubmeta(book: int):
    '''
    Generate the filename for the given book's epub metadata.

    Args:
        `book` (int):
            The given book

    Returns:
        `filename` (str): 
            The filename for the given book's epub metadata.
    '''
    return f"epub-meta{book}.yaml"

class DefaultDoc(Document):
    book = IntField()
    from_format = StringField(default="html")
    to_format = StringField(default="epub")
    output_file = StringField()
    standalone = StringField(default="true")
    self_contained = StringField(default="true")
    toc = StringField(default="true")
    toc_depth = IntField(default=2)
    epub_chapter_level = IntField(default=2)
    epub_cover_image = StringField()
    epub_fonts = ListField(StringField())
    metadata_files = ListField(StringField())
    css = StringField(default="style.css")
    input_files = ListField(StringField())
    resource_path = ListField(StringField())
    filename = StringField()
    filepath = StringField()
    
    def __init__(self,  book: int, output_file: str, epub_cover_image: str, metadata_files: list[str], input_files: list[str], resource_path: list[str], filename: str, filepath: str, css: str="style.css", epub_fonts: list[str]=['Century Gothic.ttf','abeatbykai.ttf','Photograph Signature.ttf'],from_format: str="html", to_format: str="epub", standalone: str="true",self_contained: str="true",toc: str="true",toc_depth: int=2, epub_chapter_level: int=2,):
        self.book = book
        self.output_file = output_file
        self.epub_cover_image = epub_cover_image 
        self.metadata_files: metadata_files
        self.input_files: input_files
        self.resource_path = resource_path
        self.filename = filename
        self.filepath = filepath
        self.css: = css
        self.epub_fonts: epub_fonts
        self.from_format = from_format 
        self.to_format = to_format
        self.standalone = standalone
        self.self_contained = self_contained
        self.toc = toc
        self.toc_depth = toc_depth
        self.epub_chapter_level = epub_chapter_level
        
@errwrap()
def 