"""
In this code we will illustrate the usage of decorators
as classmethod and instance method
"""


from functools import wraps


class Example(object):
    # Instance method
    def decorator(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print('Decorator1, as an instance method.')
            return func(*args, **kwargs)
        return wrapper

    # as a class method
    @classmethod
    def decorator2(cls, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print('Decorator2, as a class method.')
            return func(*args, **kwargs)
        return wrapper


if __name__ == '__main__':

    a = Example()

    @a.decorator
    def foo():
        return 

    @Example.decorator2
    def bar():
        return 