from os import environ

def get_osenv_bool(varname):
    """Render an environment variable as a Boolean

    Args:
        varname (str): Name of environment variable to Boolean-ize
    Returns:
        bool: The Boolean representation of the variable's current value
    """
    try:
        varname = str(varname)
    except Exception:
        raise
    val = environ.get(varname, '0')
    try:
        val = int(val)
    except ValueError:
        val = 0
    return bool(val)

def debug_mode():
    """Determine if the code should implement debugging behaviors

    Returns:
        bool: Boolean value of `LOCALONLY`
    """
    return get_osenv_bool('LOCALONLY')
