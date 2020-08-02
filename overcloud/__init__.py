from functools  import update_wrapper as _uw
from .items import CloudFunction, MessageQueue


def _deco_constructor(cls):
    def _ctor(*args, **kwargs):
        def _wrapper(func):
            return cls(*args, **kwargs, func=func)
        return _wrapper
    return _ctor

cloud_function = _deco_constructor(CloudFunction)
