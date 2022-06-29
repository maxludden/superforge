# superforge/core/default.py
#> Imports
import os
import sys

from dotenv import load_dotenv
from icecream import ic
from mongoengine import Document
from mongoengine.fields import IntField, ListField, StringField
from pymongo import MongoClient

try:
    import core.book as book_
    import core.chapter as chapter_
    import core.endofbook as eob_
    import core.myaml as myaml
    import core.section as section_
    import core.titlepage as titlepage_
    from core.atlas import BASE, sg
    from core.book import Book
    from core.log import errwrap, log
except ImportError:
    import book as book_
    import chapter as chapter_
    import endofbook as eob_
    import myaml
    import section as section_
    import titlepage as titlepage_
    from atlas import BASE, sg
    from book import Book
    from log import errwrap, log
#> End of Imports

class Default(Document):
    book = IntField(required=True)
    output= StringField() # the filename of the final epub file with extension
    input_files = ListField(StringField()) 
        # ordered list of the coverpage, titlepage, section(s) and its/their chapters, and end of book page.
    resource_path = ListField(StringField())
        # A list of all of the elements used to create and format the given book
    filename = StringField() # filename of the default doc (with extension)
    filepath = StringField() # The full filepath of the default doc
    meta = {'collection': 'default'}


#> MongoDB
load_dotenv()
URI = os.environ.get('Superforge')
client:MongoClient=MongoClient(URI)
make_supergene = client['make-supergene']
#< End of MongoDB


#> Functions
@errwrap() #. Verified
def get_output_file(book: int, test: bool=False):
    '''
    Generate the output-file for the given book.

    Args:
        `book` (int):
            The given book.
        `test` (bool):
            Whether the function is being tested.

    Returns:
        `output_file` (str): 
            The output-file for the given book.
    '''
    books = make_supergene['book']
    result = books.find_one({'book':book})
    output_file = result['output']
    return output_file


@errwrap() #. Verified
def get_cover_image(book: int, test: bool=False):
    '''
    Retrieve the filename of the given book's cover image from MongoDB.

    Args:
        `book` (int):
            The given book.
        `test` (bool):
            Whether the function is being tested.
            
    Return:
        'cover' (str):
            The filename of the given book's cover image.
    '''
    
    books = make_supergene['book']
    result = books.find_one({'book':book})
    cover = result['cover']
    return cover


@errwrap() #.Verified
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


@errwrap() #. Verified
def generate_meta_filename(book: int):
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


@errwrap() #. Verified
def generate_epubmeta_filename(book: int):
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


@errwrap() #. Verified
def generate_section_count(book: int):
    '''
    Determine the number of sections in a given book.
    
    Args:
        `book` (int):
            The given book.
    
    Returns:
        `section_count` (int): 
            The number of sections in a given book.
    '''
    section = make_supergene['section']
    sections = []
    results = section.find({'book':book})
    for result in results:
        sections.append(result['section'])
    log.debug(f"Sections in Book {book}: {sections}")
    return len(sections)


@errwrap()
def generate_section_files(input_section: int, filepath: bool=False):
    '''
    Generate an ordered list of the files in a given section.

    Args:
        `input_section` (int):
            The given section.
        `filepath` (bool, optional): 
            Weather to return the full filepath or just the filename. Defaults to False.

    Returns:
        `section_files` (list[str]): 
            An ordered list of the given section's files.
    '''
    #> Collections [section & chapters]
    sections = make_supergene['section']
    chapters = make_supergene['chapter']
    
    #> Declare Empty Return Variable
    section_files = []
    
    #> Generate the full filepath rather than just the filename
    if filepath:
        
        #> Section Page
        section_doc = sections.find_one({'section': input_section})
        section_filepath = section_doc['html_path']
        section_files.append(section_filepath) #< End of Section Page
        
        #> Chapters
        section_chapters = chapters.find({'section': input_section})
        for chapter_doc in section_chapters:
            chapter_filepath = chapter_doc['html_path']
            section_files.append(chapter_filepath)
        
        return section_files
    
    #> Generate just the filename and file extension
    else:
        
        #> Section Page
        section_doc = sections.find_one({'section': input_section})
        section_filename = section_doc['filename']
        section_page = f"{section_filename}.html"
        section_files.append(section_page)
        
        #> Chapters
        section_chapters = chapters.find({'section': input_section})
        for chapter_doc in section_chapters:
            chapter_filename = chapter_doc['filename']
            chapter_page = f"{chapter_filename}.html"
            section_files.append(chapter_page)
        
        return section_files

section_files = generate_section_files(1, filepath=True)
for x, file in enumerate(section_files, start=1):
    str_x = str(x).zfill(4)
    print(f'{str_x}. {file}')