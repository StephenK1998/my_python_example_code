"""
This is a decorator used for logging.
"""


import logging
from functools import wraps


def my_logging(level, name=None, message=None):
    """Add logging to a function."""
    def decorator(func):
        """The decorator function packed with extra parameters."""
        logname = name if name else func.__module__
        log = logging.getLogger(logname)
        logmsg = message if message else func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            log.log(level, logmsg)
            return func(*args, **kwargs)
        return wrapper
    return decorator


if __name__ == '__main__':
    @my_logging(logging.CRITICAL)
    def add(x, y):
        return x + y
    


