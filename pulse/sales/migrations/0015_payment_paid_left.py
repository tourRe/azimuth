# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-05 18:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0014_auto_20161105_1745'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='paid_left',
            field=models.PositiveIntegerField(default=0, null=True),
        ),
    ]