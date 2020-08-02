
class CloudFunction:

    __deploy__ = True

    def __init__(self, name=None, func=None, requirements=None):
        self.func = func
        self.name = name or func.__name__
        self.requirements = requirements or []

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)