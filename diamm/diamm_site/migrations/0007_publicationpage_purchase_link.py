# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-18 17:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diamm_site', '0006_auto_20161218_1704'),
    ]

    operations = [
        migrations.AddField(
            model_name='publicationpage',
            name='purchase_link',
            field=models.URLField(blank=True),
        ),
    ]