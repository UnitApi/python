"""
unitapi package initialization.
"""

from ._version import __version__
from . import core
from . import devices

__all__ = [
    "__version__",
    "core",
    "devices",
]
