# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-23 16:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('diamm_data', '0009_auto_20161226_2039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compositionbibliography',
            name='bibliography',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='compositions', to='diamm_data.Bibliography'),
        ),
        migrations.AlterField(
            model_name='compositionbibliography',
            name='composition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bibliography', to='diamm_data.Composition'),
        ),
    ]
