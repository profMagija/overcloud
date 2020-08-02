import os
import dill
import json
from python_terraform import Terraform as TfCli

from ..terraform import Terraform

dill.settings['recurse'] = True


class GcpBackend:
    def __init__(self, config):
        self.config = config
        self.project = config.backend_config.project
        self.tf = Terraform()
        self.tf.provider(
            'google',
            project=self.project,
            region=config.backend_config.get('region', 'us-central1')
        )

    def deploy(self):
        os.makedirs('.overcloud', exist_ok=True)
        with open('.overcloud/plan.tf.json', 'w') as planfile:
            json.dump(self.tf.to_dict(), planfile, indent=2)
        cli = TfCli(working_dir='.overcloud')
        cli.init(capture_output=False)
        cli.apply(capture_output=False)


def get_backend(config=None):
    global BACKEND
    if config is not None:
        BACKEND = GcpBackend(config)

    return BACKEND
