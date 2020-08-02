import random
import string


class PullSubscription:
    def __init__(self, queue, name):
        self.queue = queue
        self.name = name
        self.messages = []

    def __message__(self, data):
        self.messages.append(data)

    def pull(self, max_messages=0):
        if max_messages == 0:
            msgs = self.messages.copy()
            self.messages.clear()
        else:
            msgs = self.messages[:max_messages]
            del self.messages[:max_messages]

        return msgs


class PushSubscription:
    def __init__(self, queue, name, target):
        self.queue = queue
        self.name = name
        self.target = target

    def __message__(self, data):
        self.target(data)


class MessageQueue:

    def __init__(self, topic_name):
        self.topic_name = topic_name
        self._subs = []

    def subscribe(self, sub_name=None, target=None):
        if sub_name is None:
            sub_name = random.choices(string.ascii_lowercase, k=10)

        if target is None:
            subs = PullSubscription(self, sub_name)
        else:
            subs = PushSubscription(self, sub_name, target)
        self._subs.append(subs)
        return subs

    def publish(self, data):
        for sub in self._subs:
            sub.__message__(data)
