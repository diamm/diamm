# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-26 07:21
from __future__ import unicode_literals

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('diamm_site', '0021_auto_20170324_0223'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publicationpage',
            name='purchase_link',
        ),
        migrations.AlterField(
            model_name='publicationpage',
            name='pricing',
            field=wagtail.core.fields.StreamField((('price', wagtail.core.blocks.StructBlock((('description', wagtail.core.blocks.CharBlock()), ('price', wagtail.core.blocks.DecimalBlock()), ('purchase_link', wagtail.core.blocks.URLBlock())), template='website/blocks/pricing_field.jinja2')),)),
        ),
    ]
