import os
import re

from .filetype import FileTypeError
from . import rules
from . import mime

def infer_filetype(filename):
    """Determines canonical 'type' of a file"""
    if not os.path.exists(filename):
        raise OSError(filename + ' does not exist or is not accessible')
    try:
        return rules.infer(filename)
    except FileTypeError:
        return mime.infer(filename)
    except Exception as exc:
        raise FileTypeError('Failed to infer type for {}'.format(filename), exc)

