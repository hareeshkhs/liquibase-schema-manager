import os


def calculate_version():
    DEFAULT_VERSION = "v1.0.0"

    tag = os.getenv("TAG")
    version = tag or DEFAULT_VERSION

    return version


__version__ = calculate_version()
