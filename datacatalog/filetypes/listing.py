import os
import re
from pprint import pprint

from .filetype import FileType, FileTypeError
from . import rules
from . import mime

def listall(filter_attrname=None):
    big_list = rules.listall() + mime.listall()
    if filter_attrname is None:
        return big_list
    else:
        filtered_listing = [l.get(filter_attrname) for l in big_list]
        filtered_listing = list(set(filtered_listing))
        filtered_listing = sorted(filtered_listing)
        return filtered_listing

def listall_labels():
    return listall('label')

def listall_comments():
    return listall('comment')
