import stat
from xdg import Mime
from .filetype import FileType, FileTypeError
from .unknown import UnknownFileType

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
    mime = get_type_optimized(filename)
    # print('MIME', mime)
    if str(mime) == 'application/octet-stream':
        return UnknownFileType()
    else:
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

def get_type_optimized(path, follow=False):
    mtypes = sorted(Mime.globs.all_matches(path),
                    key=(lambda x: x[1]), reverse=True)
    if mtypes:
        max_weight = mtypes[0][1]
        i = 1
        for mt, w in mtypes[1:]:
            if w < max_weight:
                break
            i += 1
        mtypes = mtypes[:i]
        if len(mtypes) == 1:
            return mtypes[0][0]

        possible = [mt for mt, w in mtypes]
    else:
        possible = None

    # Break if we have a named-based candidate
    if mtypes:
        return mtypes[0][0]

    t = None
    try:
        t = Mime.magic.match(path, possible=possible)
    except IOError:
        t = None

    if t:
        return t
    elif mtypes:
        return mtypes[0][0]
    else:
        return Mime.text if Mime.is_text_file(path) else Mime.octet_stream
