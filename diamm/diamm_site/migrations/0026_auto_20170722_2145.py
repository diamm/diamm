# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-22 21:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diamm_site', '0025_auto_20170716_1222'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contentpage',
            name='tmpl',
            field=models.FilePathField(blank=True, match='.*\\.jinja2', max_length=255, null=True, path='/srv/www.diamm.ac.uk/webapps/diamm/diamm/templates/website/cms/content_page', verbose_name='Template'),
        ),
    ]