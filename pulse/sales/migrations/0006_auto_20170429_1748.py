# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-04-29 17:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0005_auto_20170429_1744'),
    ]

    operations = [
        migrations.RenameField(
            model_name='agent',
            old_name='aid',
            new_name='uid',
        ),
        migrations.AlterField(
            model_name='agent',
            name='category',
            field=models.CharField(choices=[('A', 'Agent'), ('F', 'Freelancer'), ('M', 'Manager'), ('D', 'Distributor'), ('H', 'HQ'), ('O', 'Other')], max_length=1, null=True),
        ),
    ]