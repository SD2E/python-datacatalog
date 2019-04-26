from .filetype import to_file_type

AnyFileType = to_file_type(label='*',
                           comment='Any known type')

def listall():
    """Get "*" FileType

    Returns:
        list: the "*" FileType, but in a list context
    """
    alltypes = list()
    alltypes.append(AnyFileType)
    return alltypes
