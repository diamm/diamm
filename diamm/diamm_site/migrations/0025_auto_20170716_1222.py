# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-07-16 12:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diamm_site', '0024_merge_20170708_2235'),
    ]

    operations = [
        migrations.AddField(
            model_name='problemreport',
            name='internal_note',
            field=models.TextField(blank=True, help_text='DIAMM Staff notes', null=True),
        ),
        migrations.AlterField(
            model_name='contentpage',
            name='tmpl',
            field=models.FilePathField(blank=True, match='.*\\.jinja2', max_length=255, null=True, path='/Users/ahankins/Documents/code/git/diamm/diamm/templates/website/cms/content_page', verbose_name='Template'),
        ),
    ]
