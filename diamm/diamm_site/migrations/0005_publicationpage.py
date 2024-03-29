# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-18 17:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0032_add_bulk_delete_page_permission'),
        ('wagtailimages', '0016_deprecate_rendition_filter_relation'),
        ('diamm_site', '0004_contentpage_cover_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublicationPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('body', wagtail.fields.RichTextField()),
                ('pricing', wagtail.fields.StreamField((('description', wagtail.blocks.CharBlock()), ('price', wagtail.blocks.IntegerBlock())))),
                ('cover_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtailimages.Image')),
            ],
            bases=('wagtailcore.page',),
        ),
    ]
