import sys
from pathlib import Path
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))
try:
    sys.path.remove(str(parent))
except ValueError:  # Already removed
    pass

import config
from .schemas import get_all_schemas
from .schema import JSONSchemaBaseObject
from .schema import camel_to_snake
