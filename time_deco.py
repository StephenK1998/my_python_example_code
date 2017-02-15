from functools import wraps
from time import time


def timeit(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        end = time()
        duration = end - start
        print("Executing {} costs {}.".format(func.__name__, duration))
        return result
    return decorator


