
def get_backend(name, config):
    return __import__(name, globals(), locals(), (), 1).get_backend(config)