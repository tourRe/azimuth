# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-12 16:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0018_auto_20161105_2344'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='perfect_date',
            field=models.DateTimeField(null=True, verbose_name='perfect disable date'),
        ),
    ]