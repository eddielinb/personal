from django.forms import (ModelForm, Form, BaseModelFormSet,
                          modelformset_factory,
                          ModelChoiceField,
                          HiddenInput)
from django.forms.formsets import DELETION_FIELD_NAME

from .models import Config, TestConfig, PastTest
from utils.form_fields import MacField


class PendingForm(Form):

    add_mac = MacField(label='Mac Address',
                       required=False,
                       initial="0000000000000000",
                       placeholder="0000000000000000")
    add_config = ModelChoiceField(label='Test Configuration',
                                  required=False,
                                  queryset=Config.objects.all(),
                                  empty_label=None)


class TestDetailForm(Form):
    show_mac = ModelChoiceField(label="Mac Address",
                                required=False,
                                queryset=PastTest.objects.values_list('mac', flat=True).distinct()
                                )

    show_config = ModelChoiceField(label="Test Configuration",
                                   required=False,
                                   queryset=Config.objects.all(),
                                   empty_label=None)


class ConfigForm(ModelForm):
    prefix = 'config_name'

    class Meta:
        model = Config
        fields = ('name',)


class BaseTestConfigModelFormSet(BaseModelFormSet):
    def add_fields(self, form, index):
        super(BaseTestConfigModelFormSet, self).add_fields(form, index)
        form.fields[DELETION_FIELD_NAME].widget = HiddenInput()

TestConfigFormSet = modelformset_factory(TestConfig,
                                         formset=BaseTestConfigModelFormSet,
                                         # form=TestConfigForm,
                                         fields=('status',
                                                 'request',
                                                 'next_status',
                                                 'response'),
                                         extra=1,
                                         can_delete=True)


