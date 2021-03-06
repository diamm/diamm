# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-23 09:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diamm_data', '0005_item_item_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='legacy_composition',
            field=models.CharField(blank=True, help_text='Used only to record a composition that has been converted to an item-only record', max_length=32, null=True),
        ),
    ]
