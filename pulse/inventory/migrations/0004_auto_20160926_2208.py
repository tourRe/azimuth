# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-26 22:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_auto_20160926_2207'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='destination',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='destination', to='inventory.Warehouse'),
        ),
    ]
