import os
import sys
import logging
from enum import Enum
from .. import settings

__all__ = ['get_logger']

LOG_NAME = 'persister'


class LogFormatter(object):
    STANDARD = logging.Formatter('%(name)s.%(levelname)s: %(message)s')
    VERBOSE = logging.Formatter(("%(levelname)s in %(filename)s:%(funcName)s "
                                 "at line %(lineno)d occured at %(asctime)s\n\n\t%(message)s\n\n"
                                 "Full Path: %(pathname)s\n\nProcess Name: %(processName)s"))


def get_logger(module_name=None, level=None, verbose=False):
    if module_name is None:
        module_name = __name__
    if level is None:
        level = settings.LOG_LEVEL
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.getLevelName(level))
    loghandler = logging.StreamHandler()
    if verbose is True:
        loghandler.setFormatter(LogFormatter.VERBOSE)
    else:
        loghandler.setFormatter(LogFormatter.STANDARD)
    if len(logger.handlers) <= 0:
        logger.addHandler(loghandler)
    return logger
