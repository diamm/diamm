# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-20 17:19
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('diamm_site', '0011_dissertationpage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dissertationpage',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
    ]
