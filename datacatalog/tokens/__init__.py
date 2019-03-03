__version__ = '0.6.1'
from .salt import generate_salt
from .token import get_token, validate_token
from .admin import get_admin_token, validate_admin_token, get_admin_lifetime
