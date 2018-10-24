
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *

from os import environ

name = "datacatalog"

from . import constants
from . import identifiers
from . import jsonschemas
from . import utils
from . import mongo

from . import linkedstores
from . import pathmappings
from . import filetypes
from . import agavehelpers

# from .main import *

# # from .constants import *
# from .posixhelpers import *
# from .agavehelpers import from_agave_uri, AgaveError
# from . import identifiers
# from . import filetypes

def debug_mode():
    if environ.get('LOCALONLY', None) is not None:
        return True
    else:
        return False
