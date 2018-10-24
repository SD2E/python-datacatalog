from os import environ

def debug_mode():
    if environ.get('LOCALONLY', '0') == '1':
        return True
    else:
        return False
