# Generated by Django 2.2.11 on 2020-06-06 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diamm_data', '0003_auto_20180423_1802'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='set',
            options={'ordering': ('type', 'cluster_shelfmark')},
        ),
        migrations.AddField(
            model_name='source',
            name='open_images',
            field=models.BooleanField(default=False, help_text='Source Images are available without login'),
        ),
        migrations.AlterField(
            model_name='source',
            name='public_images',
            field=models.BooleanField(default=False, help_text='Source Images are Public (with login)'),
        ),
        migrations.AlterField(
            model_name='sourcecopyist',
            name='type',
            field=models.IntegerField(blank=True, choices=[(1, 'Music'), (2, 'Text'), (3, 'Indexer'), (4, 'Liminary Text'), (5, 'Illuminator'), (6, 'Text and Music'), (7, 'Unknown')], null=True),
        ),
        migrations.AlterField(
            model_name='sourceidentifier',
            name='type',
            field=models.IntegerField(choices=[(2, 'RISM'), (3, 'CCM'), (4, 'Other catalogues/source'), (5, 'olim (Former shelfmark)'), (6, 'Alternative names')]),
        ),
    ]
