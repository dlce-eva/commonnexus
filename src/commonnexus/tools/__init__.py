"""
Tools are callables accepting a :class:`commonnexus.Nexus` object as first argument, and return
a :class:`commonnexus.Nexus` instance (either a manipulated version of the input object, or a new
instance).
"""
from .binarise import binarise  # noqa: F401
from .normalise import normalise  # noqa: F401
