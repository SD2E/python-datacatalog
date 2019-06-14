import os
from .constants import LOG_LEVEL as DEFAULT_LOG_LEVEL

LOG_LEVEL = os.environ.get('LOG_LEVEL', DEFAULT_LOG_LEVEL)
