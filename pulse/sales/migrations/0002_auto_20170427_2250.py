# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-04-27 22:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0001_squashed_0028_auto_20170427_2229'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='agent',
            name='uid',
        ),
        migrations.AlterField(
            model_name='agent',
            name='label',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='agent',
            name='login',
            field=models.CharField(max_length=30),
        ),
    ]
