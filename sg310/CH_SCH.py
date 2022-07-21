# SG3.10/CH_SCH.py

# Dependencies
from mongoengine import Document, connect, disconnect_all
from mongoengine.fields import (
    BooleanField,
    StringField,
    DateTimeField,
    IntField,
    ListField,
    URLField
)
from datetime import datetime
from json import load, dump
import logging

GEM_SRC = "https://i.imgur.com/FhWsZat.gif"
AUTH_PATH = "JSON/authkey.json"
LOG_PATH = "logs/edits.log"
CSS_SRC = "https://github.com/maxludden/SG3.10/blob/2254a1295dac4db9203d933751dd63d269b479e9/Draft%20Docs/Styles/sg.css"
BOOK_PATH = "JSON/book.json"
DRAFT_PATH = "JSON/drafts.json"
SECTION_PATH = "JSON/section.json"

# Declaire logger
log = logging.getLogger()
log.setLevel(logging.INFO)
db_file_handler = logging.FileHandler(LOG_PATH, mode="w")
log.addHandler(db_file_handler)
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s: %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)


# Defining Documents
class Chapter(Document):
    chapter = IntField(Required=True, unique=True)
    title = StringField(Required=True, max_length=200)
    original_text = StringField(Required=True)
    text = StringField()
    final_text = StringField()
    url = URLField(Required=True)
    css = StringField(max_length=200)
    tags = ListField(StringField(max_length=50), default=list)
    added = DateTimeField(default=datetime.now)
    image = StringField(max_length=200)
    head = StringField(max_length=800)
    section = IntField()
    book = IntField()
    atx = StringField(max_length=500)
    html = StringField()
    edited = BooleanField()


class Section(Document):
    title = StringField(Required=True, max_length=200)
    section = IntField(Required=True, unique=True)
    css = StringField(max_length=200)
    header3 = StringField(max_length=300)
    image = StringField(max_length=200)
    text = StringField()
    filename = StringField()
    body = StringField()
    book = IntField()
    atx = StringField(max_length=300)
    

# Func to log and print a message
def lp(msg):
    msg = str(msg)
    log.info(msg)
    print(msg)
    
def atlas_auth(*key):
    with open ("JSON/authkey.json", 'r') as infile:
        atlas_authkey = dict((load(infile)))
    if key:
         match key:
            case "user":
                return atlas_authkey["user"]
            case "password":
                return atlas_authkey["password"]
            case "uri":
                return atlas_authkey["uri"]
            case "uri_":
                return atlas_authkey["uri_"]
            case _:
                print("Error: Key not found.")
    else:
         return atlas_authkey
       
def connect_atlas():
    # Read Auth Credentials from file
    with open ("JSON/authkey.json", 'r') as infile:
        atlas_authkey = dict((load(infile)))
    URI = atlas_authkey["atlas"]["uri"]
    
    disconnect_all()
    lp("Connecting to Atlas MongoDB Cluster...")
    try:
        connect("supergene", host=URI)
        lp("\tSuccess!\n\t\tHost: cluster0.7yzr5.mongodb.net")
        lp("\t\tUsing Supergene Database")
    except:
        lp("Unable to connect to Atlas Cluster...")
        lp("\t\tQuiting Script.")

def connect_local():
    disconnect_all()
    lp("Connecting to MongoDB's local server...")
    try:
        connect("supergene", host="mongodb://localhost", port=27017)
        lp("\tSuccess!\n\t\tHost: mongodb://127.0.0.1:27017")
        lp("\t\tUsing Supergene Database")
    except:
        lp("Unable to connect to the MongoDB server on localhost...")
        lp("\t\tQuiting Script.")
        
with open(SECTION_PATH, 'r') as sec_json:
    section_dict = dict((load(sec_json)))
    
