# core/atlas.py
import re
import os
import sys
from typing import Optional

from mongoengine import connect, disconnect, disconnect_all, register_connection
from dotenv import load_dotenv

from core.log import log, errwrap

# .########################################################################
# .                                                                       #
# .         e Y8b       d8   888                                          #
# .       d888b Y8b   d88888 888 "8" 888 C88b      888 888b  Y8b Y8P      #
# .      d888888888b   888   888 ,ee 888  Y88D d8b 888 888P   Y8b Y       #
# .     d8888888b Y8b  888   888 "88 888 d,dP  Y8P 888 88"     888        #
# .                                                888         888        #
# .                                                888         888        #
# .                                                                       #
# .######################################################################## 

load_dotenv()

@errwrap(entry=False, exit=False)
def get_uri(database: str='make-supergene'):
    """Generates the connection URI for MongoDB Atlas.
    Args:
        `database` (Optional[str]):
            The alternative database you would like to connect to. Default is 'make-supergene'.
            
    Returns:
        `URI` (str):
            The atlas connection URI.
    """
    
    # > Retrieve secrets
    try:
        URI = os.environ.get("URI")
        user = os.environ.get("ATLAS_USERNAME")
        pswd = os.environ.get("ATLAS_PASSWORD")
        db = os.environ.get("ATLAS_DATABASE")
    except AttributeError as ae:
        log.error()
    
    URI = URI.replace("USERNAME",user).replace("PASSWORD",pswd).replace("DATABASE",db)
    
    return URI

@errwrap()
def sg(database: str="make-supergene"):
    """Custom Connection function to connect to MongoDB Database
    
    Args:
        `database` (Optional[str]):
            The alternative database you would like to connect to. Default is 'make-supergene'.
    """
    
    URI = get_uri(database)
    try:
        connect(database, host=URI)
        log.debug(f"Connected to MongoDB!")
    except Exception as e:
        log.warning(f"Unable to Connect to MongoDB. Error {e}")
        sys.exit(
            {
                -1: {
                    "error": f"{e}",
                    "desc": f"Unable to connect to MongoDB in Atlas' Cloud.",
                }
            }
        )

@errwrap()
def max_title(title: str):
    """Custom title case function.

    Args:
        title (str): The string you want to transform.

    Returns:
        str: The transformed string.
    """

    title = title.lower()
    articles = [
        "a",
        "an",
        "and",
        "as",
        "at",
        "but",
        "by",
        "en",
        "for",
        "if",
        "in",
        "nor",
        "of",
        "on",
        "or",
        "per",
        "the",
        "to",
        "vs",
    ]
    word_list = re.split(" ", title)
    final = [str(word_list[0]).capitalize()]
    for word in word_list[1:]:
        word = str(word)
        final.append(word if word in articles else word.capitalize())

    result = " ".join(final)

    return result