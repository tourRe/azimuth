# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-04 12:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0020_payment_is_upfront'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='unlock_date',
            field=models.DateTimeField(null=True, verbose_name='unlock date'),
        ),
    ]