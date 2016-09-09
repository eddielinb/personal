import json
import ast
from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from django.core.exceptions import ValidationError


def parse_string(json_string):
    return json.dumps(_parse_string(json_string), cls=DjangoJSONEncoder)


def _parse_string(json_string):
    try:
        # return json_string
        # print type(json.loads(json_string))
        return json.loads(json_string)
    except ValueError:
        # print "Json Fail, trying python"
        try:
            # print type(ast.literal_eval(json_string))
            python_object = ast.literal_eval(json_string)
            if isinstance(python_object, dict):
                return python_object
            else:
                raise ValidationError("Not python dict")
        except SyntaxError:
            raise ValidationError("JSON conversion error")


class JSONField(models.TextField):
    """
    JSONField is a generic textfield that neatly serializes/unserializes
    JSON objects seamlessly.
    Django snippet #1478

    example:
        class Page(models.Model):
            data = JSONField(blank=True, null=True)


        page = Page.objects.get(pk=5)
        page.data = {'title': 'test', 'type': 3}
        page.save()
    """
    def from_db_value(self, value, expression, connection, context):
        # print "from_db_value: {}, {}".format(type(value), value)
        if value is None:
            return value
        return parse_string(value)

    def to_python(self, value):
        # print "to_python: {}, {}".format(type(value), value)
        if value is None:
            return value
        if value == "":
            return None
        if isinstance(value, dict):
            return value
        if isinstance(value, basestring):
            return parse_string(value)
        raise ValidationError("JSON error")

    def get_db_prep_save(self, value, *args, **kwargs):
        # print "get_db_prep_save: {}, {}".format(type(value), value)
        if value == "":
            return None
        if isinstance(value, dict):
            value = json.dumps(value, cls=DjangoJSONEncoder)
            # print type(value)
        return super(JSONField, self).get_db_prep_save(value, *args, **kwargs)


class StatusField(models.IntegerField):
    pass


class MacField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.pop('max_length', None)
        super(MacField, self).__init__(*args, max_length=16, **kwargs)
