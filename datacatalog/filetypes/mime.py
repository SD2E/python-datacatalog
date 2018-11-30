from xdg import Mime
from .filetype import FileType, FileTypeError

try:
    Mime._cache_database()
except Exception:
    pass

def infer(filename):
    """Infer the FileType for a file by MIME classifier

    Args:
        filename (str): An absolute file path

    Returns:
        FileType: What kind of file it is
    """
    mime = Mime.get_type2(filename)
    return FileType(mimetype=mime)

def listall():
    """Get all FileTypes defined by the FreeDesktop MIME database

    Returns:
        list: Multiple FileType objects
    """
    alltypes = list()
    for t in Mime.types.items():
        alltypes.append(FileType(mimetype=t[1]))
    return alltypes
