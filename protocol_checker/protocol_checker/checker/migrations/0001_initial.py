# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-22 10:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CheckingProcedure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mac', models.CharField(max_length=16)),
                ('timestamp', models.IntegerField()),
                ('status', models.IntegerField()),
                ('request', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='CompletedTests',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mac', models.CharField(max_length=16)),
                ('timestamp', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ConfigController',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField()),
                ('request', models.CharField(max_length=30)),
                ('response', models.CharField(max_length=30)),
                ('next_status', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ConfigTables',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='CurrentController',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mac', models.CharField(blank=True, max_length=16, null=True)),
                ('status', models.IntegerField()),
                ('timestamp', models.IntegerField(blank=True, null=True)),
                ('config', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='checker.ConfigTables')),
            ],
        ),
        migrations.AddField(
            model_name='configcontroller',
            name='config',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='checker.ConfigTables'),
        ),
        migrations.AddField(
            model_name='completedtests',
            name='config',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='checker.ConfigTables'),
        ),
        migrations.AddField(
            model_name='checkingprocedure',
            name='config',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='checker.ConfigTables'),
        ),
    ]
