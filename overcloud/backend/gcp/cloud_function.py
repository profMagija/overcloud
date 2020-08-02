from base64 import b64encode
import hashlib
import os
from tempfile import NamedTemporaryFile
from zipfile import ZipFile

import dill

import overcloud
from ...items import cloud_function
from .backend import get_backend


def _hash(x):
    if isinstance(x, str):
        x = x.encode('utf-8')
    return b64encode(hashlib.sha256(x).digest()).decode('ascii')


def dumper(x):
    return repr(b64encode(dill.dumps(x)))


def make_code(func):
    return '\n'.join([
        'from base64 import b64decode as __b',
        'from dill import loads as __a',
        # 'import sys as __c',
        # f'__c.modules["overcloud"]=__a(__b({dumper(__cloud__)}))',
        f'__entry=__a(__b({dumper(func)}))'
    ])


class GcpCloudFunction(cloud_function.CloudFunction):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._deploy(get_backend())

    def _deploy(self, backend):
        backend.tf.resource(
            'google_storage_bucket', 'cf-storage-bucket',
            name=f'overcloud-{backend.config.name}-cfsrc',
        )

        function_code = make_code(self.func)
        with NamedTemporaryFile(suffix='.zip', delete=False) as srcfile:
            with ZipFile(srcfile, 'w') as zip_file:
                zip_file.writestr(
                    'main.py',
                    function_code
                )
                zip_file.writestr(
                    'requirements.txt',
                    '\n'.join([
                        'dill',
                        'google-cloud-pubsub'
                    ] + self.requirements)
                )
                zip_file.write(
                    os.path.join(os.path.dirname(__file__), '__cloud__.py'),
                    'overcloud.py'
                )
            srcfilename = srcfile.name

        safehash = _hash(function_code).replace('/', '_').replace('=', '')

        backend.tf.resource(
            'google_storage_bucket_object', f'cf-{self.name}-source',
            name=f'overcloud-cf-{self.name}-src-{safehash}.zip',
            bucket='${google_storage_bucket.cf-storage-bucket.name}',
            source=srcfilename
        )

        backend.tf.resource(
            'google_cloudfunctions_function', self.name,
            name=f'{backend.config.name}-{self.name}',
            runtime='python37',
            description=self.description,
            entry_point='__entry',
            source_archive_bucket='${google_storage_bucket.cf-storage-bucket.name}',
            source_archive_object=f'${{google_storage_bucket_object.cf-{self.name}-source.name}}',
            trigger_http=True,
            available_memory_mb=self.memory,
            environment_variables={
                'OC_HASH': _hash(function_code)
            },
            depends_on=[f'google_storage_bucket_object.cf-{self.name}-source']
        )

        if self.public:
            backend.tf.resource(
                'google_cloudfunctions_function_iam_member', f'{self.name}-invoker',
                project=f'${{google_cloudfunctions_function.{self.name}.project}}',
                region=f'${{google_cloudfunctions_function.{self.name}.region}}',
                cloud_function=f'${{google_cloudfunctions_function.{self.name}.name}}',
                role="roles/cloudfunctions.invoker",
                member="allUsers",
            )


cloud_function.CloudFunction = GcpCloudFunction
overcloud.cloud_function = overcloud._deco_constructor(GcpCloudFunction)
