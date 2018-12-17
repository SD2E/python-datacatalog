import os
import sys
import inspect
import json
import copy
import datetime
import base64
from pprint import pprint

from .store import LinkedStore
from agavepy.agave import Agave
from ...agavehelpers import AgaveHelper, AgaveError, AgaveHelperError

__all__ = ['AgaveClient', 'DocumentAgaveClient', 'AgaveError', 'AgaveHelperError']

class AgaveClient(LinkedStore):
    """Adds use of AgaveHelper to a LinkedStore"""

    def __init__(self, mongodb, config={}, session=None, agave=None, **kwargs):
        if agave is not None:
            if isinstance(agave, Agave):
                setattr(self, '_helper', AgaveHelper(agave))
            else:
                raise AgaveError(
                    '{}.init() failed due to invalid "agave" parameter'.format(
                        self.__class__.__name__))
        else:
            setattr(self, '_helper', None)
        super().__init__(mongodb, config=config, session=session, **kwargs)

class DocumentAgaveClient(object):
    """Enables use of AgaveHelper by LinkedDocument"""

    def __init__(self, agave=None, *args, **kwargs):
        if agave is not None:
            if isinstance(agave, Agave):
                setattr(self, '_helper', AgaveHelper(agave))
            else:
                raise AgaveError(
                    '{}.init() failed due to invalid "agave" parameter'.format(
                        self.__class__.__name__))
        else:
            setattr(self, '_helper', None)
        super().__init__(*args, **kwargs)
