import re
import os
from .filetype import to_file_type, FileTypeError
from .ruleset import FILETYPES

def listall():
    """Get all FileTypes defined by rules

    Returns:
        list: Multiple FileType objects
    """
    alltypes = list()
    for rule in FILETYPES:
        alltypes.append(to_file_type(label=rule[0], comment=rule[1]))
    return alltypes

def infer(filename):
    """Infer the FileType for a file by rule

    Args:
        filename (str): An absolute or relative file path

    Raises:
        FileTypeError: File did not match any of the rules

    Returns:
        FileType: What kind of file it is
    """
    fname = os.path.basename(filename)
    for label, comment, globs in FILETYPES:
        for g in globs:
            if re.compile(g, re.IGNORECASE).search(fname):
                return to_file_type(label=label, comment=comment)
    raise FileTypeError('File matched no type classifcation rules')
