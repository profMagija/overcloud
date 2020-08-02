
def get_backend(name):
    return __import__(name, globals(), locals(), (), 1)