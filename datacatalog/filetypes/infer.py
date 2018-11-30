import os
import re

from .filetype import FileTypeError, FileTypeLabel
from . import rules
from . import mime

def infer_filetype(filename, check_exists=True):
    """Infer a file's canonical ``file type``

    Args:
        filename (str): An absolute or relative file path
        check_exists (bool, optional): Verify the file exists before classifying it

    Note:
        Use of ``check_exists`` requires ``filename`` to be an absolute path

    Raises:
        OSError: Existence of the target file cannot be verified
        FileTypeError: The target file's type could not be inferred

    Returns:
        FileTypeLabel: a ``type`` for the file
    """
    try:
        return rules.infer(filename)
    except FileTypeError:
        if check_exists:
            if not os.path.exists(filename):
                raise OSError(filename + ' does not exist or is not accessible')
        return mime.infer(filename)
    except Exception as exc:
        raise FileTypeError('Failed to infer type for {}'.format(filename), exc)
