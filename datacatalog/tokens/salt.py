import os
import base64

def generate_salt():
    salt = os.urandom(16)
    return str(base64.b64encode(salt).decode('utf-8'))
