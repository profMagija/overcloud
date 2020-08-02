
class CloudFunction:

    __deploy__ = True

    def __init__(self, name=None, func=None, requirements=None, description=None, memory=256, public=False):
        self.func = func
        self.name = name or func.__name__
        self.requirements = requirements or []
        self.description = description or getattr(func, '__doc__', '')
        self.memory = memory
        self.public = public

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def deploy(self, name):
        return self.func

import dill

def _dill_cloud_function(cf):
    return dill.Pickler.dispatch[type(cf.func)](cf.func)

dill.pickle(CloudFunction, _dill_cloud_function)
