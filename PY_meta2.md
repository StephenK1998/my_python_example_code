-------------
Title: Python 元编程(2)
-------------

注：示例代码地址： [Example_code](https://github.com/StephenK1998/my_python_example_code)

# 装饰器与类

## Note1： 在一个类中定义一个装饰器

我们可以在类中定义一个装饰器， 并将其作用于其他的函数或方法。

``` python
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
```

标准库中的@property就是类中定义装饰器的一个很好的例子。当需要在装饰器背后记录或合并信息， 那么类内的装饰器就是一种选择。值得一提的是类内定义的装饰器只需要在外层的方法或函数中加上cls与self。


## Note 2: 把装饰器定义成类

在Python界，曾经就有人呼吁应当把所有的装饰器都声明成一个类，这样做才是正确的。诚然，这样的做法确实有其优越性，但是相比函数式的装饰器，也多了复杂性。

``` python
import types
from functools import wraps


class Profiled:
    def __init__(self, func):
        wraps(func)(self) (1)
        self.ncalls = 0

    def __call__(self, *args, **kwargs):
        self.ncalls += 1
        return self.__wrapped__(*args, **kwargs)

    def __get__(self, instance, cls): (2)
        if instance is None:
            return self
        else:
            return types.MethodType(self, instance) 
```
这段代码难理解的地方主要就是(1) 与(2).
（1）中，wraps(func)返回一个携带了func信息的functools.partial,然后再把它绑定到self上;
(2) 中， \__get__为描述符协议，作用是将方法绑定到instance上。

## Note 3: 用装饰器为类打补丁

``` python
def log_attribute(cls):

    orig_getattribute = cls.__getattribute__

    def new_getattribute(self, name):
        print("Log")
        return orig_getattribute
    
    cls.__getattribute__ = new_getattribute
```