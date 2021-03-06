# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-05 17:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0013_payment_credit_after'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='credit_before',
            field=models.FloatField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='paid_after',
            field=models.PositiveIntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='payment',
            name='credit_after',
            field=models.FloatField(default=0, null=True),
        ),
    ]
