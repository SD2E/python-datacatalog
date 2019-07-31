"""Exposes a Text-oriented AnnotationManager via a messaging interface
"""

EVENT_NAMES = ('create', 'delete', 'reply')

from .manager import TextAnnotationManager
from . import schemas
from .schemas import get_schemas
