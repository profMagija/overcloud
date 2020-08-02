from ..terraform import Terraform
from tempfile import NamedTemporaryFile
from zipfile import ZipFile
from base64 import b64encode
from pprint import pprint
import dill
from python_terraform import Terraform as TfCli, IsFlagged
import json
import os


class backend:
    def __init__(self, config):
        self.config = config
        self.tf = Terraform()
        self.tf.provider(
            'google',
            project=config.backend_config.project,
            region=config.backend_config.get('region', 'us-central1')
        )

    def register(self, item):
        fn = getattr(self, 'register_' + type(item).__name__, None)

        if fn:
            fn(item)
        else:
            raise TypeError(type(item))

    def register_CloudFunction(self, cf):
        self.tf.resource(
            'google_storage_bucket', 'cf-storage-bucket',
            name=f'overcast-{self.config.name}-cfsrc',
        )

        data = dill.dumps(cf.func)
        with NamedTemporaryFile(suffix='.zip', delete=False) as srcfile:
            with ZipFile(srcfile, 'w') as zip_file:
                zip_file.writestr(
                    'main.py',
                    f"from base64 import b64decode as __a;from dill import loads as __b;__entry=__b(__a({repr(b64encode(data))}))"
                )
                zip_file.writestr(
                    'requirements.txt',
                    '\n'.join(['dill'] + cf.requirements)
                )
            srcfilename = srcfile.name

        self.tf.resource(
            'google_storage_bucket_object', f'cf-{cf.name}-source',
            name=f'overcast-cf-{cf.name}-src.zip',
            bucket='${google_storage_bucket.cf-storage-bucket.name}',
            source=srcfilename
        )

        self.tf.resource(
            'google_cloudfunctions_function', cf.name,
            name=f'{self.config.name}-{cf.name}',
            runtime='python37',
            entry_point='__entry',
            source_archive_bucket='${google_storage_bucket.cf-storage-bucket.name}',
            source_archive_object='${google_storage_bucket_object.cf-' +
            cf.name + '-source.name}',
            trigger_http=True,
        )

    def deploy(self):
        os.makedirs('.overcast', exist_ok=True)
        with open('.overcast/plan.tf.json', 'w') as planfile:
            json.dump(self.tf.to_dict(), planfile, indent=2)
        cli = TfCli(working_dir='.overcast')
        cli.init(capture_output=False)
        cli.apply(capture_output=False)
