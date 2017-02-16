from inspect import signature
from functools import wraps


def typeassert(*ty_args, **ty_kwargs):
    def decorate(func):
        # Disable if not in debug mode
        if not __debug__:
            return func

        sig = signature(func)
        bound_types = sig.bind_partial(*ty_args, **ty_kwargs).arguments  # ->This is an ordereddict

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_values = sig.bind(*args, **kwargs)
            for name, val in bound_values.arguments.items():
                if name in bound_types:
                    if not isinstance(val, bound_types[name]):
                        raise TypeError(
                            'Arguemnt {} must be {} type'.format(name, bound_types[name])
                        )
            return func(*args, **kwargs)
        return wrapper
    return decorate


@typeassert(int, int)
def add(x, y):
    return x + y


if __name__ == '__main__':
    try:
        add(2, "hello")
    except TypeError as e:
        print("Successfully implement typeassert decorator!")