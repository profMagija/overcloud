from ..terraform import Terraform
from tempfile import NamedTemporaryFile
from zipfile import ZipFile
from base64 import b64encode
from pprint import pprint
import dill
from python_terraform import Terraform as TfCli, IsFlagged
import json
import os
import hashlib

dill.settings['recurse'] = True


def _hash(x):
    if isinstance(x, str):
        x = x.encode('utf-8')
    return b64encode(hashlib.sha256(x).digest()).decode('ascii')


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
            raise TypeError(type(item).__name__)

    def register_CloudFunction(self, cf):
        self.tf.resource(
            'google_storage_bucket', 'cf-storage-bucket',
            name=f'overcloud-{self.config.name}-cfsrc',
        )

        function_code = f'from base64 import b64decode as __b;from dill import loads as __a;__entry=__a(__b({repr(b64encode(dill.dumps(cf.deploy(cf.name))))}))'
        with NamedTemporaryFile(suffix='.zip', delete=False) as srcfile:
            with ZipFile(srcfile, 'w') as zip_file:
                zip_file.writestr(
                    'main.py',
                    function_code
                )
                zip_file.writestr(
                    'requirements.txt',
                    '\n'.join(['dill'] + cf.requirements)
                )
            srcfilename = srcfile.name

        safehash = _hash(function_code).replace('/', '_').replace('=', '')

        self.tf.resource(
            'google_storage_bucket_object', f'cf-{cf.name}-source',
            name=f'overcloud-cf-{cf.name}-src-{safehash}.zip',
            bucket='${google_storage_bucket.cf-storage-bucket.name}',
            source=srcfilename
        )

        self.tf.resource(
            'google_cloudfunctions_function', cf.name,
            name=f'{self.config.name}-{cf.name}',
            runtime='python37',
            description=cf.description,
            entry_point='__entry',
            source_archive_bucket='${google_storage_bucket.cf-storage-bucket.name}',
            source_archive_object=f'${{google_storage_bucket_object.cf-{cf.name}-source.name}}',
            trigger_http=True,
            available_memory_mb=cf.memory,
            environment_variables={
                'OC_HASH': _hash(function_code)
            },
            depends_on=[f'google_storage_bucket_object.cf-{cf.name}-source']
        )

        if cf.public:
            self.tf.resource(
                'google_cloudfunctions_function_iam_member', f'{cf.name}-invoker',
                project=f'${{google_cloudfunctions_function.{cf.name}.project}}',
                region=f'${{google_cloudfunctions_function.{cf.name}.region}}',
                cloud_function=f'${{google_cloudfunctions_function.{cf.name}.name}}',
                role="roles/cloudfunctions.invoker",
                member="allUsers",
            )

    def deploy(self):
        os.makedirs('.overcloud', exist_ok=True)
        with open('.overcloud/plan.tf.json', 'w') as planfile:
            json.dump(self.tf.to_dict(), planfile, indent=2)
        cli = TfCli(working_dir='.overcloud')
        cli.init(capture_output=False)
        cli.apply(capture_output=False)
