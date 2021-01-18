#!/usr/bin/env python3
import argparse
from getpass import getpass
from datacatalog.tokens import get_admin_token, validate_token
from datacatalog.tokens.exceptions import InvalidToken

def main():
    parser = argparse.ArgumentParser(
        prog="python -m scripts.token",
        description="Generate an admin token.")

    parser.add_argument("--key",
                        help="Provide admin token key on CLI",
                        type=str, dest='apikey')

    args = parser.parse_args()
    if args.apikey is not None:
        apikey = args.apikey
    else:
        apikey = getpass('Admin Token Key: ')

    token = None
    try:
        token = get_admin_token(apikey)
    except Exception:
        raise

    print('Admin Token: ' + token)

if __name__ == '__main__':
    main()
