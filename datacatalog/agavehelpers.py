from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import *

import re
import os
from agavepy.agave import AgaveError

def from_agave_uri(uri=None, Validate=False):
    '''
    Parse an Agave URI into a tuple (systemId, directoryPath, fileName)
    Validation that it points to a real resource is not implemented. The
    same caveats about validation apply here as in to_agave_uri()
    '''
    systemId = None
    dirPath = None
    fileName = None
    proto = re.compile(r'agave:\/\/(.*)$')
    if uri is None:
        raise AgaveError("URI cannot be empty")
    resourcepath = proto.search(uri)
    if resourcepath is None:
        raise AgaveError("Unable resolve URI")
    resourcepath = resourcepath.group(1)
    firstSlash = resourcepath.find('/')
    if firstSlash is -1:
        raise AgaveError("Unable to resolve systemId")
    try:
        systemId = resourcepath[0:firstSlash]
        origDirPath = resourcepath[firstSlash + 1:]
        dirPath = '/' + os.path.dirname(origDirPath)
        fileName = os.path.basename(origDirPath)
        return (systemId, dirPath, fileName)
    except Exception as e:
        raise AgaveError(
            "Error resolving directory path or file name: {}".format(e))
