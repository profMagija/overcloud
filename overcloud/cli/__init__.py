import click
import config
from ..backend import get_backend
import types
import os


def _load_config():
    return config.config(
        ('env', 'OVERCLOUD_'),
        ('json', 'overcloud.json', True) if os.path.exists('overcloud.json') else ('dict', {}),
        ('yaml', 'overcloud.yaml', True) if os.path.exists('overcloud.yaml') else ('dict', {})
    )


def _iterate_items(item, callback):

    print('iterating on ', item)

    for name in dir(item):
        value = getattr(item, name)
        if not getattr(value, '__deploy__', False):
            continue
        print('iterating on ', item, name, value)

        if isinstance(value, types.ModuleType):
            _iterate_items(value, callback)
        else:
            callback(value)


@click.command('deploy')
def deploy():
    cfg = _load_config()
    print(cfg)
    backend = get_backend(cfg.backend).backend(cfg)

    entry = __import__(cfg.entry)
    _iterate_items(entry, backend.register)

    backend.deploy()


@click.group('main', commands={
    'deploy': deploy
})
def main():
    pass
