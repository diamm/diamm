# Generated by Django 3.2.18 on 2023-04-26 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diamm_data', '0008_auto_20230425_1224'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='personidentifier',
            name='person_identifier_type',
        ),
        migrations.AlterField(
            model_name='personidentifier',
            name='identifier_type',
            field=models.IntegerField(choices=[(1, 'RISM'), (2, 'VIAF'), (3, 'Wikidata'), (4, 'GND (Gemeinsame Normdatei)'), (5, 'MusicBrainz Artist'), (6, 'ORCID'), (7, 'Bibliothèque national de France'), (8, 'Library of Congress')]),
        ),
    ]