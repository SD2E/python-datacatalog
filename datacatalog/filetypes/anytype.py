from .filetype import FileType

class AnyFileType(FileType):
    def __init__(self):
        super().__init__(label='*',
                         comment='Any known type')

def listall():
    """Get "*" FileType

    Returns:
        list: the "*" FileType, but in a list context
    """
    alltypes = list()
    alltypes.append(AnyFileType())
    return alltypes
