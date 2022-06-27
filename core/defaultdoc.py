# core/defaultdoc.py
import sys

from mongoengine import Document
from mongoengine.fields import IntField, ListField, StringField

try:
    import core.book as book_
    import core.chapter as chapter_
    import core.endofbook as eob_
    import core.myaml as myaml
    import core.section as section_
    import core.titlepage as titlepage_
    from core.atlas import BASE, sg
    from core.log import errwrap, log
except ImportError:
    import book as _book
    import chapter as _chapter
    import endofbook as eob_
    import myaml
    import section as section_
    import titlepage as titlepage_
    from atlas import BASE, sg
    from log import errwrap, log


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
    

@errwrap()
def generate_output_file(book: int):
    '''
    Generate the output file's name for the given book's default doc.

    Args:
        `book` (int):
            The given book.
    Returns:
        `output` (str): 
            The filename of the given book.
    '''
    for doc in book_.Book.objects(book=book):
        return doc.output 
        # Example of doc.output: "First God's Sanctuary.epub"

@errwrap()
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
    sg()
    sections = []
    for doc in section_.Section.objects(book=book):
        sections.append(doc.section)
    section_count = len(sections)
    return section_count



@errwrap(exit=False)
def generate_section_files(section: int, filepath: bool=False):
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


@errwrap(exit=False)
def generate_input_files(book: int, filepaths: bool=False):
    '''
    Generates and ordered list of documents to be included in the given epub.

    Args:
        `book` (int):
            The given book.
            
        `filepaths` (bool, optional): 
            Boolean switch to determine whether or not to generate the filepath instead of the filename. Defaults to False.

    Returns:
        `input_files` (list[str]): 
            A list of ordered documents' filename/filepath's to be included in the given books epub output.
    '''
    input_files = []
    section_count = generate_section_count(book)
    if section_count == 1:
        if filepaths:
            #> Coverpage
            input_files.append(book_.get_filepath(book))
            
            #> Titlepage
            input_files.append(titlepage_.get_html_path(book))
            
            #> Section Page and Chapters
            section_files = generate_section_files(book, filepath=True)
            # Because only books 1, 2, and 3 have one section, the book param and section param are interchangeable. Which is why we can substitute it's book param for it's section param
            for section_file in section_files:
                input_files.append(section_file)
            
            #> End of Book
            input_files.append(eob_.get_html_path())
            return input_files      #. End Single-section Filepath
        else:
            #> Coverpage
            input_files.append(book_.get_filename(book))
            
            #> Titlepage
            input_files.append(f'{titlepage_.get_filename}.html')
            
            #> Section Page and Chapters
            section_files = generate_section_files(book)
            # Because only books 1, 2, and 3 have one section, the book param and section param are interchangeable. Which is why we can substitute it's book param for it's section param
            for section_file in section_files:
                input_files.append(section_file)
            
            #> End of Book
            input_files.append(f'{eob_.get_filename}.html')
            return input_files      #. End Single-section Filename
    else:
        if filepaths:
            #> Coverpage
            input_files.append(book_.get_filepath(book))
            
            #> Titlepage
            input_files.append(titlepage_.get_html_path)
            
            #> Sections
            sections = []
            for doc in section_.Section.objects(book=book):
                sections.append(doc.section)
                # Searches through the Sections Collection for the two sections that have the a `doc.book` == the given book.
            
            #> First section
            # Uses the python list `min()` function to return the lowest value from sections
            section_files = generate_section_files(min(sections), filepath=True)
            for section_file in section_files:
                input_files.append(section_file)
                
            #> Second section
            # Uses the python list function `max()` to return the highest value from sections
            section_files = generate_section_files(max(sections), filepath=True)
            for section_file in section_files:
                input_files.append(section_file)
                
            #> End of Book
            input_files.append(eob_.get_html_path())
            return input_files      #. End Multi-section Filepaths
        else:
            #> Coverpage
            input_files.append(book_.get_filename(book))
            
            #> Titlepage
            input_files.append(f'{titlepage_.get_filename}.html')
            
            #> Sections
            sections = []
            for doc in section_.Section.objects(book=book):
                sections.append(doc.section)
                # Searches through the Sections Collection for the two sections that have the a `doc.book` == the given book.
            
            log.info(f"Sections: {sections}")
            #> First section
            # Uses the python list min function to return the lowest value from sections
            section_files = generate_section_files(min(sections))
            for section_file in section_files:
                input_files.append(section_file)
            
            #> Second section
            # Uses the python list function `max` to return the highest value from sections
            section_files = generate_section_files(max(sections), filepath=True)
            for section_file in section_files:
                input_files.append(section_file)
            
            #> End of Book
            input_files.append(f'{eob_.get_filename}.html')
            return input_files      #. End Multi-section Filenames

@errwrap(entry=False)
def save_input_files(book: int, input_files: list[str]):
    '''
    Save the list of input files for the given book to MongoDB.

    Args:
        `input_files` (list[str]):
            An ordered list of the content files for the given book.

    Returns:
        `return_code` (int): 
            An integer value associated with the completion status of the script. A successful run will return `0`. An unsuccessful save will return a non `0` integer value.
    '''
    sg()
    try:
        for doc in Default.objects(book=book):
            log.debug(f"Accessed Book {book}'s Default Doc's MongoDB Document.")
            doc.input_files = input_files
            doc.save()
            log.debug(f"Updated Book {book}'s Default Doc's input files.")
        return 0
    except Exception as e:
        log.error(f"Unable to access Book {book}'s default doc Document.")
        raise e

@errwrap(exit=False)
def get_input_files(book: int):
    '''
    Retrieve the input-files for the given book's default doc from MongoDB.

    Args:
        `book` (int):
            The given book.

    Returns:
        `input_files` (list[str]): 
            An ordered list of the content documents used to create the given book.
    '''
    sg()
    for doc in Default.objects(book=book):
        input_files = doc.input_files
        if len(input_files) > 2:
            log.debug(f"Retrieved the input_files for Book {book}'s default doc.")
            return doc.input_files
        else:
            log.warning(f"Book {book}'s default doc's input files haven't been properly set. Please generate and save its input_files before attempting to access them from MongoB.")
            sys.exit({1:f"Unable to access Book {book}'s default doc's input files from MongoDB."})


@errwrap(exit=False)
def generate_resource_paths(book: int):
    rp = []
    book_dir = str(book).zfill(2)
    WDIR = f'{BASE}/books/book{book_dir}/'
    
    #. Meta Documents
    #> Working Directory
    rp.append(f'{WDIR}/.')
    
    #> CSS Stylesheet
    rp.append(f'{WDIR}/Styles/style.css')
    
    #> Embedded Fonts
    rp.append(f'{WDIR}/Styles/abeatbykai.ttf')
    rp.append(f'{WDIR}/Styles/Century Gothic.ttf')
    rp.append(f'{WDIR}/Styles/Photograph Signature.ttf')
    
    #> Images
    rp.append(f'{WDIR}/Images/title.png')
    rp.append(f'{WDIR}/Images/cover{book}.png')
    rp.append(f'{WDIR}/Images/gem.gig')
    
    #> Normal/ePub Metadata
    rp.append('f{WDIR}/html/meta{book}.yaml')
    rp.append('f{WDIR}/html/epub-meta{book}.yaml')
    
    #. Content Documents
    rp.extend(generate_input_files(book, filepaths=True))
    
    return rp


@errwrap()
def generate_html_path(book: int):
    book_str = str(book).zfill(2)
    html_path = f"{BASE}/books/book{book_str}/html/sg{book}.yaml"
    return html_path


@errwrap()
def generate_defaultdoc(book: int, test: bool=False):
    #> Shared Static Elements
    part1 = [
        {'from': 'html'},
        {'to': 'epub'}
    ]
    
    #> Output File
    output_file = generate_output_file(book)
    part2 = [{'output-file': output_file}]
    
    #> Input-files
    input_files = generate_input_files(book)
    
    #> Scope
    part3 = [
        {'standalone': 'true'},
        {'self-contained': 'true'}]
    
    #> Resource-Paths
    rp = generate_resource_paths(book)
    
    
    #> ePub Table of Contents
    part4 = [
        {'toc': 'true'},
        {'toc-depth': 2},
        '\n'
    ]
    
    #> ePub related fields
    # Fonts
    epub_fonts = [
        'abeatbykai.ttf',
        'Century Gothic.ttf',
        'Photograph Signature.ttf'
    ]
    part5 = [
        {'epub-chapter-level': 2},
        {'epub-cover-image': f'cover{book}.png'},
        {'epub-fonts': epub_fonts},
        {'epub_metadata': f'epub-meta{book}.yaml'}
    ]
    
    #> Metadata and CSS
    metadata_files = [
        'epub-meta{book}.yaml',
        'meta{book}.yaml'
    ]
    stylesheet = [
        'style.css'
    ]
    part6 = [
        {'metadata-files': metadata_files},
        {'css': stylesheet}
    ]
    python_obj = {
        [
            part1,
            part2,
            part3,
            part4,
            part5,
            part6
        ]
    }
    
    default_doc = myaml.safe_dump(python_obj,book)
    if test:
        print(default_doc)
        response = input("\n\nWould you like to save this Default Doc to disk? (Y/N)")
        if response.lower() == 'y':
            html_path = generate_html_path(book)
            with open (html_path, 'w') as outfile:
                outfile.write(default_doc)
                
        else:
            log.error("Invalid DefaultDoc. Quitting Script.")
            sys.exit(1)
    else:
        log.info(f"Finished Generating Default Doc for Book {book}.")
        
    
    
    
    

    