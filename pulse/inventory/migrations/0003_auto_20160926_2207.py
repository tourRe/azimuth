# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-26 22:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_auto_20160926_2150'),
    ]

    operations = [
        migrations.RenameField(
            model_name='transaction',
            old_name='desination',
            new_name='destination',
        ),
        migrations.AlterField(
            model_name='transaction',
            name='origin',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='origin', to='inventory.Warehouse'),
        ),
    ]
