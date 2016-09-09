from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from utils.model_fields import JSONField, StatusField, MacField


@python_2_unicode_compatible
class Request(models.Model):
    string = models.CharField(max_length=32)

    def __str__(self):
        return self.string


@python_2_unicode_compatible
class Response(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class SuccessResponse(Response):
    json_content = JSONField()


class FailResponse(Response):
    code = models.CharField(max_length=32)
    message = models.CharField(max_length=128)
    http_status = models.PositiveSmallIntegerField()


@python_2_unicode_compatible
class Config(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return str(self.name)


@python_2_unicode_compatible
class TestConfig(models.Model):
    config = models.ForeignKey(Config, on_delete=models.CASCADE)
    status = StatusField()
    request = models.ForeignKey(Request, on_delete=models.PROTECT)
    next_status = StatusField()
    response = models.ForeignKey(Response, on_delete=models.PROTECT)

    def __str__(self):
        return "'{name}': {status}/{request} -> {next}/{response}".format(
            name=self.config.name,
            status=self.status,
            request=self.request,
            next=self.next_status,
            response=self.response
        )


@python_2_unicode_compatible
class CurrentTest(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    request = models.ForeignKey(Request, on_delete=models.SET_NULL, null=True, blank=True)
    mac = MacField(blank=True, null=True)
    config = models.ForeignKey(Config, on_delete=models.PROTECT)
    status = StatusField()

    def __str__(self):
        return "{}: {}".format(self.created, self.mac)


@python_2_unicode_compatible
class CheckingProcedure(models.Model):
    mac = MacField()
    config = models.ForeignKey(Config)
    timestamp = models.IntegerField()
    status = StatusField()
    request = models.CharField(max_length=30)

    def __str__(self):
        return "{}: {}".format(self.timestamp, self.mac)


@python_2_unicode_compatible
class CompletedTest(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)

    mac = MacField()
    config = models.ForeignKey(Config, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return "{}: {}".format(self.timestamp, self.mac)

@python_2_unicode_compatible
class PastTest(models.Model):

    mac = MacField()
    timestamp = models.DateTimeField(auto_now_add=True)

    config = models.ForeignKey(Config, on_delete=models.SET_NULL, null=True)
    status = StatusField()
    request = models.ForeignKey(Request, on_delete=models.SET_NULL, null=True)
    next_status = StatusField(null=True)
    response = models.ForeignKey(Response, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "{}: {}".format(self.timestamp, self.mac)

