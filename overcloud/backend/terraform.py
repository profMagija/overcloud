class Terraform:
    def __init__(self):
        self._dict = {
            'resource': {},
            'provider': {}
        }

    def _update(self, item, name, value, kwargs):
        resource = item.setdefault(name, {})
        if value:
            resource.update(value)

        resource.update(kwargs)
        return resource

    def provider(self, p_name, p_value=None, **kwargs):
        return self._update(self._dict['provider'], p_name, p_value, kwargs)

    def resource(self, r_type, r_name, r_value=None, **kwargs):
        res_type = self._dict['resource'].setdefault(r_type, {})
        return self._update(res_type, r_name, r_value, kwargs)

    def to_dict(self):
        return self._dict
