# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-24 02:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diamm_site', '0019_publicationpage_show_on_front'),
    ]

    operations = [
        migrations.AddField(
            model_name='publicationpage',
            name='teaser',
            field=models.TextField(blank=True, null=True),
        ),
    ]
