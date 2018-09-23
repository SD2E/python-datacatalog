from .listing import listall_labels

def validate_label(label):
    """Ensure that label is valid as defined by current datacatalog.filetypes"""
    labels = listall_labels()
    if label.upper() in labels:
        return True
    return False
