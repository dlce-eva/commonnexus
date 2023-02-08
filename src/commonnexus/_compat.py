try:
    from functools import cached_property
except ImportError:  # pragma: no cover
    cached_property = property  # on py3.7 things will be a bit slower

__all__ = ['cached_property']
