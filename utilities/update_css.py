# Styles/update_css.py

import os
from subprocess import run
from time import sleep

from tqdm.auto import tqdm

from core.atlas import BASE
from core.log import errwrap, log
from utilities.yay import superyay, yay


@errwrap()
def update_css():
    CSS_MAIN = f"{BASE}/Styles/style.css"
    
    stylesheets = {
        "1": f"{BASE}/books/book01/Styles/style.css",
        "2": f"{BASE}/books/book02/Styles/style.css",
        "3": f"{BASE}/books/book03/Styles/style.css",
        "4": f"{BASE}/books/book04/Styles/style.css",
        "5": f"{BASE}/books/book05/Styles/style.css",
        "6": f"{BASE}/books/book06/Styles/style.css",
        "7": f"{BASE}/books/book07/Styles/style.css",
        "8": f"{BASE}/books/book08/Styles/style.css",
        "9": f"{BASE}/books/book09/Styles/style.css",
        "10": f"{BASE}/books/book10/Styles/style.css",
    }
    
    books = range(1,11)
    celebrate: bool = True
    for x in tqdm(books):
        log.debug(f"Updating Book {x}'s Stylesheet")
        key = str(x)
        cmd = ['cp', f'{CSS_MAIN}', f'{stylesheets[key]}']
        concat_cmd = " ".join(cmd)
        log.debug(f"CMD: {concat_cmd}")
        try:
            result = run(cmd)
        except Exception as e:
            celebrate = False
            raise Exception(e)
            
        else:
            if celebrate == True:
                celebrate = True

    if celebrate == True:
        superyay()


update_css()
