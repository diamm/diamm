# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-06-09 16:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diamm_data', '0017_auto_20170425_1722'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notation',
            options={'ordering': ('name',)},
        ),
        migrations.AlterModelOptions(
            name='set',
            options={'ordering': ('cluster_shelfmark',)},
        ),
        migrations.AlterField(
            model_name='geographicarea',
            name='legacy_id',
            field=models.ManyToManyField(blank=True, to='diamm_data.LegacyId'),
        ),
        migrations.AlterField(
            model_name='geographicarea',
            name='variant_names',
            field=models.CharField(blank=True, help_text='Separate names with a comma.', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='page_order',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='source',
            name='notations',
            field=models.ManyToManyField(blank=True, related_name='sources', to='diamm_data.Notation'),
        ),
        migrations.AlterField(
            model_name='sourcenote',
            name='type',
            field=models.IntegerField(choices=[(1, 'General Description'), (97, 'RISM Description'), (98, 'Census Catalogue of Music Description'), (4, 'Extent'), (5, 'Physical Description'), (6, 'Binding'), (7, 'Ownership'), (8, 'Watermark'), (9, 'Liminary Note'), (10, 'Notation'), (11, 'Date'), (12, 'Dedication'), (13, 'Ruling'), (14, 'Foliation'), (15, 'Decoration'), (16, 'Index'), (17, 'Surface'), (18, 'DIAMM Note'), (99, 'Private Note')]),
        ),
    ]