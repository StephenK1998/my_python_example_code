def log_attribute(cls):

    orig_getattribute = cls.__getattribute__

    def new_getattribute(self, name):
        print("Log")
        return orig_getattribute
    
    cls.__getattribute__ = new_getattribute

"""
Demo
@log_attribute
class A:
    pass

"""

