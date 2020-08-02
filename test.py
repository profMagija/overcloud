import json
from overcloud import cloud_function

@cloud_function(public=True)
def test_function(a):
    return json.dumps({'m': 'a'}), 200

print('oh')