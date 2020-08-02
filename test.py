from overcloud import cloud_function

@cloud_function('test')
def test_function(a):
    return 'Hello there!', 200