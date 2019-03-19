from collections import namedtuple
from attrdict import AttrDict
from xdg.Mime import MIMEtype

FileType = namedtuple('FileType', ['label', 'comment'])

class FileTypeError(ValueError):
    """Error that occurs when working with FileTypes"""
    pass

class FileTypeComment(str):
    """Verbose human-readable name for a file type"""
    def __new__(cls, value):
        value = str(value).title()
        return str.__new__(cls, value)

class FileTypeLabel(str):
    """Short, human-readable label for a file type"""
    def __new__(cls, value):
        value = str(value).upper()
        return str.__new__(cls, value)

def to_file_type(mimetype=None, label=None, comment=None):
    new_label = None
    new_comment = None
    if mimetype is not None and isinstance(mimetype, MIMEtype):
        new_label = mimetype.subtype
        if new_label.startswith('x-'):
            # Offsets an annoying decision by MIME catalog holder to
            # label types not registered with ICANN with the x- prefix
            new_label = str(new_label.replace('x-', ''))
        if new_label.startswith('vnd.'):
            # Offset more MIME catalog namespacing
            new_label = str(new_label.replace('vnd.', ''))
        new_label = new_label.upper()
        new_comment = mimetype.get_comment()
    elif label is not None and comment is not None:
        if isinstance(label, str) and isinstance(comment, str):
            new_label = label.upper()
            new_comment = comment
    else:
        raise FileTypeError('Invalid inputs for FileType')
    return FileType(new_label, new_comment)
