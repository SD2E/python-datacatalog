__version__ = '0.6.0'

from .filetype import to_file_type, FileTypeError
from .infer import infer_filetype
from .listing import listall, listall_labels, listall_comments
from .unknown import UnknownFileType
from .validate import validate_label

from . import anytype
from . import unknown
