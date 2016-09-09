from django.forms import CharField, IntegerField

from validators import validate_mac


class MacField(CharField):
    default_validators = [validate_mac]

    def __init__(self, placeholder="", *args, **kwargs):
        self.placeholder = placeholder
        super(MacField, self).__init__(*args, **kwargs)

    def clean(self, value):
        return super(MacField, self).clean(value).upper()


class StatusField(IntegerField):
    def __init__(self, *args, **kwargs):
        super(StatusField, self).__init__(min_value=0, *args, **kwargs)
