from .filetype import FileType

class UnknownFileType(FileType):
    def __init__(self):
        super().__init__(label='UNKNOWN',
                         comment='Unknown type (mime:application/octet-stream)')

def listall():
    """Get unknown FileType

    Returns:
        list: the Unknown FileType, but in a list context
    """
    alltypes = list()
    alltypes.append(UnknownFileType())
    return alltypes
