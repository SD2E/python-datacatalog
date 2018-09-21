from attrdict import AttrDict
from xdg import Mime

class FileType(AttrDict):
    def __init__(self, label, comment):
        self.label = label.upper()
        self.comment = comment

def infer_filetype(filename):
    return __infer_xdg_mime(filename)

def __infer_xdg_mime(filename):
    mime = Mime.get_type2(filename)
    label = mime.subtype
    if label.startswith('x-'):
        label = str(label.replace('x-', ''))
    comment = str(mime.get_comment())
    return FileType(label, comment)
