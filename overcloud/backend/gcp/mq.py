from ...items import mq
from .backend import get_backend
from .cloud_function import GcpCloudFunction
import dill

class PullSubscription:

    __module__ = 'overcloud'

    def __init__(self, queue, name):
        self.project = queue.project
        self.topic = queue.topic_name
        self.name = name
        self.full_name = f'{self.topic}-{name}'


class MessageQueue:

    __module__ = 'overcloud'

    def __init__(self, topic_name):
        self.topic_name = topic_name
        self._register(get_backend())

    def _register(self, backend):
        self.project = backend.project
        self._tf_name = f'{backend.config.name}-{self.topic_name}'
        self.full_name = f'projects/{backend.project}/topics/{self._tf_name}'
        backend.tf.resource(
            'google_pubsub_topic', self.topic_name,
            name=self._tf_name
        )

    def subscribe(self, sub_name=None, target=None):
        if sub_name is None:
            sub_name = random.choices(string.ascii_lowercase, k=10)

        if target is None:
            backend.tf.resource(
                'google_pubsub_subscription', sub_name,
                name=f'{self.topic_name}-{sub_name}',
                topic=self._tf_name
            )
            return GcpPullSubscription(self, sub_name)
        else:
            raise NotImplementedError

import overcloud

overcloud.MessageQueue = MessageQueue
overcloud.PullSubscription = PullSubscription