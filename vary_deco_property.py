import logging
from functools import wraps, partial


"""
About partial function:
functools.partial(func, *args, **keywords)
Return a new partial object which when called will behave like func called with the positional arguments args and keyword arguments keywords. If more arguments are supplied to the call, they are appended to args. If additional keyword arguments are supplied, they extend and override keywords. Roughly equivalent to:

def partial(func, *args, **keywords):
    def newfunc(*fargs, **fkeywords):
        newkeywords = keywords.copy()
        newkeywords.update(fkeywords)
        return func(*args, *fargs, **newkeywords)
    newfunc.func = func
    newfunc.args = args
    newfunc.keywords = keywords
    return newfunc
The partial() is used for partial function application which “freezes” some portion of a function’s arguments and/or keywords resulting in a new object with a simplified signature. For example, partial() can be used to create a callable that behaves like the int() function where the base argument defaults to two:

>>>
>>> from functools import partial
>>> basetwo = partial(int, base=2)
>>> basetwo.__doc__ = 'Convert base 2 string to an int.'
>>> basetwo('10010')
18

"""


def attach_wrapper(obj, func=None):
    if not func:
        return partial(attach_wrapper, obj)
    setattr(obj, func.__name__, func)
    return func


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

        @attach_wrapper(wrapper)
        def set_level(newlevel):
            nonlocal level
            level = newlevel

        @attach_wrapper(wrapper)
        def set_msg(newmsg):
            nonlocal logmsg
            logmsg = newmsg

        return wrapper
    return decorator


"""
DEMO:

>>> @my_logging(logging.DEBUG)
def add(x, y):
    return x + y

>>> add.set_msg("hahaha")
>>> add(2, 3)
DEBUG:__main__:hahaha
5

"""

if __name__ == '__main__':
    @my_logging(logging.CRITICAL)
    def add(x, y):
        return x + y

    add.set_msg("hahaha")
    add(2,3)