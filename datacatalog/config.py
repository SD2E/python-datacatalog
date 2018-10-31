from os import environ

def get_osenv_bool(varname):
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
    return get_osenv_bool('LOCALONLY')
