class PullSubscription:
    def pull(self, max_messages=0):
        from google.cloud.pubsub import SubscriberClient
        subscriber = SubscriberClient()
        sub_path = subscriber.subscription_path(self.project, self.full_name)
        if max_messages == 0:
            response = subscriber.pull(sub_path)
        else:
            response = subscriber.pull(sub_path, max_messages=max_messages)
        ack_ids = [msg.ack_id for msg in response.received_messages]
        if ack_ids:
            subscriber.acknowledge(sub_path, ack_ids)
        return [m.message.data for m in response.received_messages]


class MessageQueue:
    def publish(self, data):
        from google.cloud.pubsub import PublisherClient
        client = PublisherClient()
        sub_path = client.topic_path(self.project, self._tf_name)
        client.publish(sub_path, data).result()
