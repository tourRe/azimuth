# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-01 09:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0003_auto_20161001_0904'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='status',
            field=models.CharField(choices=[('a', 'Activated'), ('d', 'Deactivated'), ('u', 'Unlocked'), ('w', 'Written Off')], max_length=1),
        ),
    ]
