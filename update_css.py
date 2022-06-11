# Styles/update_css.py

from core.atlas import get_base
from tqdm.auto import trange
from core.log import log


BASE = get_base()
CSS_MAIN = f'{BASE}/Styles/style.css'


log.debug("Updating CSS...")
with open (CSS_MAIN, 'r') as infile:
    CSS = infile.read()
    
    
for book in trange((1, 11),unit="book", desc="Updating CSS"):
    
    book_zfill = str(book).zfill(2)
    css_path = f'{BASE}books/book{book_zfill}/Styles/style.css'
    log.debug(f"Writing to path: {css_path}")
    
    with open (css_path, 'w') as outfile:
        outfile.write(CSS)
        
    log.debug(f"Updated Book {book}'s CSS.")