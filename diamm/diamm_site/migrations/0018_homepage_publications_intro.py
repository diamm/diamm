# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-23 09:18
from __future__ import unicode_literals

from django.db import migrations
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('diamm_site', '0017_auto_20170123_1608'),
    ]

    operations = [
        migrations.AddField(
            model_name='homepage',
            name='publications_intro',
            field=wagtail.wagtailcore.fields.RichTextField(blank=True, null=True),
        ),
    ]
