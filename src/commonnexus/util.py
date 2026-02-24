"""
Utility functions
"""
from typing import Optional
import logging


def log_or_raise(msg: str, log: Optional[logging.Logger] = None, level='error') -> bool:
    """Log an error or raise a ValueError."""
    if log is None:
        raise ValueError(msg)
    getattr(log, level)(msg)
    return False


def do_until_stopiteration(func, *args, **kw):
    """Helper to consume an iterator."""
    while 1:
        try:
            func(*args, **kw)
        except StopIteration:
            break
