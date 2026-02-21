"""
Utility functions
"""
import typing
import logging


def log_or_raise(msg: str, log: typing.Optional[logging.Logger] = None, level='error') -> bool:
    """Log an error or raise a ValueError."""
    if log is None:
        raise ValueError(msg)
    getattr(log, level)(msg)
    return False
