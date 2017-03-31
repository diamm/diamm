# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-20 17:19
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0032_add_bulk_delete_page_permission'),
        ('wagtaildocs', '0007_merge'),
        ('diamm_site', '0010_auto_20161220_1646'),
    ]

    operations = [
        migrations.CreateModel(
            name='DissertationPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('abstract', wagtail.wagtailcore.fields.RichTextField()),
                ('university', models.CharField(max_length=255)),
                ('year', models.IntegerField()),
                ('degree', models.CharField(max_length=64)),
                ('attachment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='wagtaildocs.Document')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            bases=('wagtailcore.page',),
        ),
    ]
