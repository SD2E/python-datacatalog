"""Typed UUID identifiers for managed collections

A typed UUID is a UUID5 generated from one or more plaintext 
string identifiers. Each managed document has a typed 
UUID field 'uuid`. 

These are called 'typed UUID' because the three-digit prefix 
for a given UUID denotes which managed document type it refers 
to. This design allows the datacatalog package to quickly 
determine which collection (and managing class) should 
be used for a given document.

The three-digit type prefixes are defined in 
typeduuid.uuidtypes submodule.

In addition to defining UUID types, other functions of 
this submodule include operations to generate JSONschema 
definitions for each type, create and validate typed UUIDs, 
convert to other UUID formats such as HashId. 
"""

from .schemas import get_schemas
from . typeduuid import *
