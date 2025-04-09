import os

def calculate_version():
    DEFAULT_VERSION = "v1.0.0"

    tag = os.getenv("TAG")
    ci_prdtag = os.getenv("CI_PRDTAG")
    version = ci_prdtag or tag or DEFAULT_VERSION
    
    return version

__version__ = calculate_version()
