from overcloud import cloud_function, MessageQueue

pubsub = MessageQueue('data')

@cloud_function(public=True)
def test_function(a):
    pubsub.publish(str(a).encode('utf-8'))

@cloud_function(trigger=pubsub)
def other_function(event, context):
    print(event)
