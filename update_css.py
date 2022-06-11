# Styles/update_css.py

import os
import webbrowser
from subprocess import run
from time import sleep

import requests
from tqdm.auto import tqdm

from core.atlas import get_base
from core.log import errwrap, log


@errwrap()
def update_css():
    CSS_MAIN = "/Users/maxludden/dev/py/superforge/Styles/style.css"
    
    stylesheets = {
        "1": "/Users/maxludden/dev/py/superforge/books/book01/Styles/style.css",
        "2": "/Users/maxludden/dev/py/superforge/books/book02/Styles/style.css",
        "3": "/Users/maxludden/dev/py/superforge/books/book03/Styles/style.css",
        "4": "/Users/maxludden/dev/py/superforge/books/book04/Styles/style.css",
        "5": "/Users/maxludden/dev/py/superforge/books/book05/Styles/style.css",
        "6": "/Users/maxludden/dev/py/superforge/books/book06/Styles/style.css",
        "7": "/Users/maxludden/dev/py/superforge/books/book07/Styles/style.css",
        "8": "/Users/maxludden/dev/py/superforge/books/book08/Styles/style.css",
        "9": "/Users/maxludden/dev/py/superforge/books/book09/Styles/style.css",
        "10": "/Users/maxludden/dev/py/superforge/books/book10/Styles/style.css",
    }
    
    for x in range (1,11):
        log.debug(f"Updating Book {x}'s Stylesheet")
        key = str(x)
        cmd = ['cp', f'{CSS_MAIN}', f'{stylesheets[key][2]}']
        concat_cmd = " ".join(cmd)
        log.debug(f"CMD: {concat_cmd}")
        try:
            result = run(cmd)
        except Exception as e:
            raise Exception(e)
        else:
            if result.returncode == 0:
                os.system('open raycast://confetti\necho "Celebrate  🎉"')
                # sleep(1)
                # os.system('open raycast://confetti\necho Celebrate  🎉"')


update_css()
