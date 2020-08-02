# Overcloud - a simple way to make clouds

<dl>
<dt>overcloud</dt>
<dd>To cover with clouds. To become cloudy.</dd>
</dl>

## Installation

Be sure you have `terraform`, and authorized to use the cloud platform of your choice (GCP only right now). Then do
```bash
pip install overcloud
```
and overcloud should be installed.

## Example usage

Create a `overcloud.yaml` file in a new directory, containing:

```yaml
# we will be using GCP for this, make sure you are logged in
# currently, only `gcp` is implemented
backend: gcp

# entry point file, in module syntax
entry: cloud

# name of the project, make sure its relatively-unique
name: YOUR_NAME-testing

# this is backend-specific configuration, we only specify the GCP project
backend_config:
  project: YOUR-PROJECT
```

This is your config file. Mostly used for static configuration

```py
# import all the goodies
from overcloud import *

# Create a new cloud function, and set it to public.
# By default, it's HTTP-triggered
@cloud_function(public=True)
def test_function(req):
    # return some nice message
    return 'Hello, World!', 200
```

The `req` is a `flask.Request`-like object.

After that, you can say
```sh
overcast deploy
```
in your shell, and answer 'yes' when prompted. If all goes well, 'terraform' (which is used in the background) should deploy all the resources (may take a while).

Now you can reach your cloud function at `https://us-central1-YOUR_PROJECT.cloudfunctions.net/YOUR_NAME-testing-test_function`
