"""
Now that pkg_resources is deprecated, all the stuff that's needed to
use the supposed replacement importlib deserves its own file here.
"""

import atexit
import contextlib
import importlib.resources

file_manager = contextlib.ExitStack()
atexit.register(file_manager.close)


def resource_filename(package: str, file_name: str) -> str:
    """Similar functionality to now-deprecated pkg_resources.resource_filename() call"""
    ref = importlib.resources.files(package) / file_name
    return str(file_manager.enter_context(importlib.resources.as_file(ref)))


def resource_string(package: str, file_name: str) -> str:
    ref = importlib.resources.files(package) / file_name
    return ref.read_text()


__all__ = [
    "resource_filename",
    "resource_string",
]
