# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-04-27 22:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0026_agent_com'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='ID',
            field=models.CharField(default='US000000', max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='agent',
            name='location',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='agent',
            name='manager',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='sales.Manager'),
        ),
        migrations.AlterField(
            model_name='agent',
            name='warehouse',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.Warehouse'),
        ),
    ]
