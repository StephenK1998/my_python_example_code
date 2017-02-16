-------------------
title: Python3 元编程(1)
-------------------

注：示例代码地址： [Example_code](https://github.com/StephenK1998/my_python_example_code)

# 一： 装饰器

装饰器是Python中非常常见的一种语法糖，使用起来也非常的容易。
在Python中， A 与 B是等价的

> A: @dec def a():pass

> B: a = dec(a)

这就是装饰器的用途，给函数添加一个外部包装。
让我们来看一个最简单的装饰器例子：

``` python
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
```

这段代码非常简单，但是也展现出了一般装饰器的模式：外部处理 +　调用原函数
＋　返回闭包；需要注意wraps()函数，这是必须的，否则被装饰的函数会丢失其
所有的元数据(文档字符串、函数注解、函数名)。

## Note 1: 装饰器解包装

对于使用@wraps装饰的原函数，可以使用新函数的\__wrapped\__属性
来访问原函数.

``` python
>>> @somedecorator
... def add(x, y):
...     return x + y

>>> orig = add.__wrapped__
>>> orig(3, 4)
7
```

注意不要在未使用@wraps与多层装饰的函数上使用这项技术。

## Note 2: 带参数的装饰器

``` python
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
```

三层包装，第一眼看上去很复杂，但其实是很简单的。my_logging外层函数
包装了那些参数，使得@my_logging(...)->@decorator,其实就是一次
函数调用完成了参数的包装。带参数的装饰器在Python中经常可见，
例如Flask中的路由，包括前面一直提到的@wraps，使用带参数的decorator
是比较Pythonic的一种写法。


##　Note 3: 自定义装饰器的属性

``` python
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
```

这段代码展示了Python动态语言的优美性，在Python中，“万物皆对象”，通过将setter与getter包装成log的
属性函数， 用户可以动态修改log的level与msg。


## Note 4:使用装饰器来进行类型检查

作为动态语言，你不需要为函数的参数声明类型。然而，在某些场景下，你需要对类型进行管控，而装饰器
可以帮助你写出优雅简洁的类型检查代码。

### 1. 使用inspect.signature
想要编写这样的一个装饰器，我们就必须要有能对参数签名进行检查的手段。好在Python为我们提供了inspect
模块，让我们可以轻松完成任务。

```python
from inspect import signature 导入了模块
def spam(x, y, z=3):
    return

sig = signature(spam)    函数签名对象
sig.parameters -> mappingproxy对象，一个有x,y,z的OrderedDict

sig.parameters['z'].name -> 'z'
sig.parameters['z'].default -> 3

bound_types = sig.bind_partial(int, z=int) 对x与z进行类型强制绑定

bound_values = sig.bind(1, 2, 3) 绑定值

实现类型断言
for name, val in bound_values.arguments.items():
    if name in bound_types.arguments:
        if not isinstance(val, bound_types.arguments[name]):
            raise TypeError()

```

接下来我们实现typeassert装饰器：

```python
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

```
