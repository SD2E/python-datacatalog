from slugify import slugify

def encode_title(textstring, separator=':', stopwords=[], case_insensitive=False):
    return separator.join(slug for slug in slugify(
        textstring, stopwords=stopwords,
        lowercase=case_insensitive).split('-'))
