# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-30 07:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_auto_20160926_2208'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='label',
            field=models.CharField(max_length=30, null=True),
        ),
    ]
