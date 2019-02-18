from .listing import listall_labels
from .filetype import FileTypeLabel, FileTypeError

def validate_label(label, permissive=True):
    """Verify a string label is found in the known set of FileTypeLabels

    Args:
        label (str): A value to check
        permissive (bool, optional): Whether to raise an Exception on failure

    Returns:
        bool: Whether ``label`` is valid
    """
    labels = listall_labels()
    if label.upper() in labels:
        return True
    else:
        if permissive is True:
            return False
        else:
            raise FileTypeError(
                "{} is not a known FileTypeLabel".format(label))
