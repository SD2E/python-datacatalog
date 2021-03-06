import os
import re
from pprint import pprint

from .filetype import to_file_type, FileTypeError, FileTypeLabel, FileTypeComment
from . import rules
from . import mime
from . import unknown
from . import anytype

def listall(filter_attrname=None):
    """Lists rule- and MIME-based types, labels, or comments

    Args:
        filter_attrname (str, optional): Attribute name to extract from list

    Returns:
        list: A list of FileType, FileTypeLabel, or FileTypeComment objects
    """
    big_list = rules.listall() + mime.listall() + unknown.listall() + anytype.listall()
    if filter_attrname is None:
        return big_list
    else:
        if filter_attrname == 'label':
            filtered_listing = [FileTypeLabel(l.label) for l in big_list]
        elif filter_attrname == 'comment':
            filtered_listing = [FileTypeComment(l.comment) for l in big_list]
        filtered_listing = list(set(filtered_listing))
        filtered_listing.sort()
        return filtered_listing

def listall_labels():
    """Lists rule-based labels

    Returns:
        list: A list of FileTypeLabels
    """
    return listall('label')

def listall_comments():
    """Lists rule-based labels

    Returns:
        list: A list of FileTypeComments
    """
    return listall('comment')
