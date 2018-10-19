# TODO: This needs to live in the database
MAPPINGS = {'0': '/uploads/',
            '1': '/products/',
            '2': '/products/',
            'Reference': '/reference/'
            }

from .levels import prefix_for_level, level_for_prefix, level_for_filepath
