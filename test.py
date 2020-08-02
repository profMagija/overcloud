import json
from overcloud import cloud_function, MessageQueue

pubsub = MessageQueue('data')

@cloud_function(public=True)
def test_function(a):
    print('here')
    pubsub.publish(str(a).encode('utf-8'))
    print('there')
