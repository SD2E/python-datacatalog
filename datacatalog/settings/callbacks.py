import os

__all__ = []

# Callback targets
# TODO - These are in anticipation of webhook support on given actions
# Email target
DEFAULT_CALLBACK_EMAIL = os.environ.get(
    'CATALOG_CALLBACK_EMAIL', 'bounces@devnull.com')
# POST target
DEFAULT_CALLBACK_URI = os.environ.get(
    'CATALOG_CALLBACK_URI', 'https://devnull.com/')
