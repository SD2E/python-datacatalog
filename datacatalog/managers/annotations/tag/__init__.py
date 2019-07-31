"""Exposes a Tag-oriented AnnotationManager via a messaging interface
"""

EVENT_NAMES = ('create', 'delete', 'link', 'unlink')

from .manager import TagAnnotationManager
from . import schemas
from .schemas import get_schemas
