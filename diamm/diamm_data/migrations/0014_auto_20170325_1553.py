# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-25 15:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diamm_data', '0013_auto_20170323_0724'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personnote',
            name='type',
            field=models.IntegerField(choices=[(1, 'Biography'), (2, 'Variant Name'), (3, 'Date'), (4, 'Bibliography')]),
        ),
    ]