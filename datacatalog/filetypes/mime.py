import os
import re
from pprint import pprint
from xdg import Mime
from .filetype import FileType, FileTypeError

try:
    Mime._cache_database()
except Exception:
    pass

def infer(filename):
    mime = Mime.get_type2(filename)
    return FileType(mimetype=mime)

def listall():
    """Return a list of FileType objects defined by XDG MIME database"""
    l = []
    for t in Mime.types.items():
        l.append(FileType(mimetype=t[1]))
    return l
