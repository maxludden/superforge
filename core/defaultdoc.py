# core/defaultdoc.py
from yaml import load_all, SafeLoader, SafeDumper
from mongoengine import Document
from mongoengine.fields import IntField, StringField

from core.atlas import sg, max_title, ROOT
from core.log import log, errwrap