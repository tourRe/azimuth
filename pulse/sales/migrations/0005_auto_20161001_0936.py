# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-01 09:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0004_auto_20161001_0918'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='status',
            field=models.CharField(choices=[('e', 'Activated'), ('d', 'Deactivated'), ('u', 'Unlocked'), ('w', 'Written Off')], max_length=1),
        ),
    ]
