import os
from version import __version__ as default_version

def calculate_version():
    tag = os.getenv("TAG")
    return tag if tag else default_version

__version__ = calculate_version()
