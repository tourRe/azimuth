# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-03-26 20:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0025_complan'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='com',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='sales.ComPlan'),
        ),
    ]
