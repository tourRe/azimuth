# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-04-29 17:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0004_auto_20170428_0045'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='manager',
            name='gender',
        ),
        migrations.AddField(
            model_name='manager',
            name='is_active',
            field=models.NullBooleanField(),
        ),
    ]