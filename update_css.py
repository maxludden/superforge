# Styles/update_css.py

from tqdm.auto import tqdm

from core.atlas import get_base
from core.log import errwrap, log


@errwrap()
def update_css():
    BASE = get_base()
    CSS_MAIN = f'{BASE}/Styles/style.css'

    log.debug("Updating CSS...")
    with open (CSS_MAIN, 'r') as infile:
        CSS = infile.read()
    
    books = range(1,11)
    for book in tqdm(books, unit="book", desc="Updating CSS"):
        
        book_zfill = str(book).zfill(2)
        css_path = f'{BASE}books/book{book_zfill}/Styles/style.css'
        log.debug(f"Writing to path: {css_path}")
        
        with open (css_path, 'w') as outfile:
            outfile.write(CSS)
            
        log.debug(f"Updated Book {book}'s CSS.")
        
update_css()
