from attrdict import AttrDict
from xdg.Mime import MIMEtype

class FileTypeError(ValueError):
    """Error that occurs when working with FileTypes"""
    pass

class FileTypeComment(str):
    """Verbose human-readable name for a file type"""
    def __new__(cls, value):
        value = str(value).lower()
        return str.__new__(cls, value)

class FileTypeLabel(str):
    """Short, human-readable label for a file type"""
    def __new__(cls, value):
        value = str(value).lower()
        return str.__new__(cls, value)

class FileType(AttrDict):
    """Defines a ``type`` that a file can be"""

    def __init__(self, mimetype=None, label=None, comment=None):
        if mimetype is not None and isinstance(mimetype, MIMEtype):
            label = mimetype.subtype
            if label.startswith('x-'):
                # Offsets an annoying decision by MIME catalog holder to
                # label types not registered with ICANN with the x- prefix
                label = str(label.replace('x-', ''))
            if label.startswith('vnd.'):
                # Offset more MIME catalog namespacing
                label = str(label.replace('vnd.', ''))
            self.label = label.upper()
            self.comment = mimetype.get_comment()
        elif label is not None and comment is not None:
            if isinstance(label, str) and isinstance(comment, str):
                self.label = label.upper()
                self.comment = comment
            else:
                raise FileTypeError('Failed to create a FileType from inputs')
        else:
            raise FileTypeError('Failed to create a FileType from inputs')
