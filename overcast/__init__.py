from .items import CloudFunction


def cloud_function(*args, **kwargs):
    def _wrapper(func):
        return CloudFunction(*args, **kwargs, func=func)
    return _wrapper
