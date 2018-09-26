from attrdict import AttrDict
from xdg.Mime import MIMEtype

class FileTypeError(ValueError):
    pass

class FileType(AttrDict):
    def __init__(self, mimetype=None, label=None, comment=None):
        print(label, comment)
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
