# core/defaultdoc.py
from yaml import load_all, SafeLoader, SafeDumper
from mongoengine import Document
from mongoengine.fields import IntField, StringField, ListField, DictField

from core.atlas import sg, max_title, ROOT
from core.log import log, errwrap
import core.book as book_
import core.section as section_
import core.titlepage as titlepage_
import core.chapter as chapter_
import core.endofbook as eob_
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
    for doc in book_.Book.objects(book=book):
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
    for doc in book_.Book.objects(book=book):
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
        self.css = css
        self.epub_fonts: epub_fonts
        self.from_format = from_format 
        self.to_format = to_format
        self.standalone = standalone
        self.self_contained = self_contained
        self.toc = toc
        self.toc_depth = toc_depth
        self.epub_chapter_level = epub_chapter_level

@errwrap()
def get_section_count(book: int):
    '''
    Determine the number of sections in a given book.

    Args:
        `book` (int):
            The given book.

    Returns:
        `section_count` (int): 
            The number of sections in a given book.
    '''
    sg()
    sections = []
    for doc in section_.Section.objects(book=book):
        sections.append(doc.section)
    section_count = len(sections)
    return section_count

@errwrap()
def get_section_files(section: int, filepath: bool=False):
    '''
    Generate the input files for a given section.

    Args:
        `section` (int):
            The given section.
            
        `filepath` (bool, optional): If you are looking for the full filepath for the given section's input files, or just the filename. Defaults to False.

    Returns:
        `section_files` (list[str]): 
            The input files of the given section.
    '''
    sg()
    for doc in section_.Section.objects(section=section):
        section_files = []
        #> Filenames
        if not filepath:
            section_page = section_.get_filename(section)
            section_files.append(f"{section_page}.html")
            for chapter in doc.chapters:
                chapter_filename = chapter_.generate_filename(chapter)
                section_files.append(f"{chapter_filename}.html)")
            log.debug(f"Generated filenames for Section Input Files for Section {section}.")
            return section_files
        #> Filepaths
        else:
            section_files.append(section_.get_html_path(section))
            for chapter in doc.chapters:
                section_files.append(chapter_.get_html_path(chapter))
            log.debug(f"Generated filepaths for Section Input Files for Section {section}.")
            return section_files

@errwrap()
def get_input_files(book: int, filepaths: bool=False):
    input_files = []
    section_count = get_section_count(book)
    if section_count == 1:
        if filepaths:
            #> Titlepage
            input_files.append(titlepage_.get_html_path)
            
            #> Section Page and Chapters
            section_files = get_section_files(book, filepath=True)
            # Because only books 1, 2, and 3 have one section, the book param and section param are interchangeable. Which is why we can substitute it's book param for it's section param
            for section_file in section_files:
                input_files.append(section_file)
            
            #> End of Book
            input_files.append(eob_.get_html_path())
            return input_files
        else:
            #> Titlepage
            input_files.append(f'{titlepage_.get_filename}.html')
            
            #> Section Page and Chapters
            section_files = get_section_files(book)
            # Because only books 1, 2, and 3 have one section, the book param and section param are interchangeable. Which is why we can substitute it's book param for it's section param
            for section_file in section_files:
                input_files.append(section_file)
            
            #> End of Book
            input_files.append(f'{eob_.get_filename}.html')
            return input_files
    else:
        if filepaths:
            #> Titlepage
            input_files.append(titlepage_.get_html_path)
            
            #> Sections
            sections = []
            for doc in section_.Section.objects(book=book):
                sections.append(doc.section)
                # Searches through the Sections Collection for the two sections that have the a `doc.book` == the given book.
            
            #> First section
            # Uses the python list `min()` function to return the lowest value from sections
            section_files = get_section_files(min(sections), filepath=True)
            for section_file in section_files:
                input_files.append(section_file)
                
            #> Second section
            # Uses the python list function `max()` to return the highest value from sections
            section_files = get_section_files(max(sections), filepath=True)
            for section_file in section_files:
                input_files.append(section_file)
                
            #> End of Book
            input_files.append(eob_.get_html_path())
            return input_files
        else:
            input_files.append(f'{titlepage_.get_filename}.html')
            
            #> Sections
            sections = []
            for doc in section_.Section.objects(book=book):
                sections.append(doc.section)
                # Searches through the Sections Collection for the two sections that have the a `doc.book` == the given book.
            
            #> First section
            # Uses the python list `min()` function to return the lowest value from sections
            section_files = get_section_files(min(sections))
            for section_file in section_files:
                input_files.append(section_file)
            
            #> Second section
            # Uses the python list function `max()` to return the highest value from sections
            section_files = get_section_files(max(sections), filepath=True)
            for section_file in section_files:
                input_files.append(section_file)
            
            input_files.append(f'{eob_.get_filename}.html')
            return input_files