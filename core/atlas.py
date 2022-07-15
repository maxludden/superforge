# core/atlas.py
import os
import re
import sys
from multiprocessing.sharedctypes import Value
from platform import platform
from typing import Optional

from dotenv import dotenv_values, load_dotenv
from mongoengine import connect, disconnect_all
from pymongo.errors import ConnectionFailure, InvalidURI, NetworkTimeout

try:
    from core.log import errwrap, log
except ImportError:
    from log import errwrap, log


@errwrap(entry=False, exit=False)
def generate_base():
    if platform() == "Linux":
        ROOT = "home"
    else:
        ROOT = "Users"  # < Mac
    BASE = f"/{ROOT}/maxludden/dev/py/superforge"
    return BASE

BASE = generate_base()


# .
# .            d8   888
# .   ,"Y88b  d88   888  ,"Y88b  dP"Y
# .  "8" 888 d88888 888 "8" 888 C88b
# .  ,ee 888  888   888 ,ee 888  Y88D
# .  "88 888  888   888 "88 888 d,dP
# .
# .


@errwrap(entry=False, exit=False)
def get_atlas_uri(database: str = "SUPERGENE"):
    """Generates the connection URI for MongoDB Atlas.
    Args:
        `database` (Optional[str]):
            The alternative database you would like to connect to. Default is 'SUPERGENE'.

    Returns:
        `URI` (str):
            The atlas connection URI.
    """
    db_lower = str(database).lower()
    if "supergene" in db_lower:
        # < Ensures that DB input is either:
        # make-supergene
        # supergene
        if "make" in db_lower:
            db = "MAKE_SUPERGENE"
        elif db_lower == "supergene":
            db = "SUPERGENE"
        else:
            raise ConnectionError(f"{database} is not a valid DB.")

    URI = os.environ.get(db)
    log.debug(f"URI retrieved from .env:\n<code>{URI}</code>")
    return URI


@errwrap(entry=False, exit=False)
def sg(database: str = "SUPERGENE"):
    """
    Custom Connection function to connect to MongoDB Database

    Args:
        `database` (Optional[str]):
            The alternative database you would like to connect to. Default is 'SUPERGENE'.
    """
    #> Get Connection URI
    disconnect_all()
    
    db_lower = str(database).lower()
    if "supergene" in db_lower:
        if "make" in db_lower:
            db = "MAKE_SUPERGENE"
        elif db_lower == "supergene":
            db = "SUPERGENE"
        else:
            raise ConnectionError(f"{database} is not a valid DB.")
    
    URI = get_atlas_uri(db)
    log.debug(f"Retrieved connection URI: {URI}")
    
    #> Attempt to connect to MongoDB    
    try:
        connect(db, host=URI)
        log.debug(f"Connected to {database}")
    except ConnectionError as ce:
        log.error(f"Connection Error: {ce}")
        raise ce
    except Exception as e:
        log.warning(f"Unable to Connect to MongoDB. Error {e}")
        raise e


@errwrap()
def max_title(title: str):
    """
    Custom title case function.

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
