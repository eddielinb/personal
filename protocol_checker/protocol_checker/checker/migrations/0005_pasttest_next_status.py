# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-06 10:14
from __future__ import unicode_literals

import checker.utils.model_fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checker', '0004_auto_20160905_1455'),
    ]

    operations = [
        migrations.AddField(
            model_name='pasttest',
            name='next_status',
            field=checker.utils.model_fields.StatusField(null=True),
        ),
    ]
