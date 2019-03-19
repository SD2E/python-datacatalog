from .filetype import to_file_type

UnknownFileType = to_file_type(label='UNKNOWN',
                               comment='Type (mime:application/octet-stream)')

def listall():
    """Get unknown FileType

    Returns:
        list: the Unknown FileType, but in a list context
    """
    alltypes = list()
    alltypes.append(UnknownFileType)
    return alltypes
