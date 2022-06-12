# core/atlas.py
import os
import re
import sys
from platform import platform
from typing import Optional

from dotenv import load_dotenv
from mongoengine import (connect, disconnect, disconnect_all,
                        register_connection)
from pymongo.errors import ConnectionFailure, InvalidURI, NetworkTimeout

from core.log import errwrap, log

load_dotenv()

@errwrap()
def generate_root():
    if platform() == 'Linux':
        ROOT = 'home'
    else:
        ROOT = 'Users' #< Mac
    return ROOT

@errwrap()
def generate_base():
    ROOT = generate_root()
    return f'/{ROOT}/maxludden/dev/py/superforge/'

#.
#.            d8   888               
#.   ,"Y88b  d88   888  ,"Y88b  dP"Y 
#.  "8" 888 d88888 888 "8" 888 C88b  
#.  ,ee 888  888   888 ,ee 888  Y88D 
#.  "88 888  888   888 "88 888 d,dP  
#.                                   
#.  


@errwrap(entry=False, exit=False)
def get_atlas_uri(database: str='make-supergene'):
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
        URI = str(os.environ.get("URI"))
        log.debug(f"URI: {URI}")
        user = os.environ.get("ATLAS_USERNAME")
        log.debug(f"user: {user}")
        pswd = os.environ.get("ATLAS_PASSWORD")
        log.debug(f"pswd: {pswd}")
        
    except AttributeError as ae:
        log.error()
    
    URI = URI.replace("USERNAME",user)
    URI = URI.replace("PASSWORD",pswd)
    URI = URI.replace("DATABASE", database)
    
    return URI

@errwrap(entry=False, exit=False)
def sg(database: str="make-supergene"):
    """
    Custom Connection function to connect to MongoDB Database
    
    Args:
        `database` (Optional[str]):
            The alternative database you would like to connect to. Default is 'make-supergene'.
    """
    
    URI = get_atlas_uri(database)
    try:
        connect(database, host=URI)
        log.debug(f"Connected to MongoDB!")
    except ConnectionError as ce:
        ConnectionError(ce)
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


@errwrap(entry=False, exit=False)
def supergene(database: str="make-supergene"):
    """
    Custom Connection function to connect to MongoDB Database
    
    Args:
        `database` (Optional[str]):
            The alternative database you would like to connect to. Default is 'make-supergene'.
    """
    
    URI = get_atlas_uri(database)
    try:
        connect(database, host=URI)
        log.info(f"Connected to MongoDB!")
    except ConnectionError as ce:
        ConnectionError(ce)
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
