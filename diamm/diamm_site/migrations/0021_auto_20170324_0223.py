# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-24 02:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diamm_site', '0020_publicationpage_teaser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publicationpage',
            name='teaser',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
