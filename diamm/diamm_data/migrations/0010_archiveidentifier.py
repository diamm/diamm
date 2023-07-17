# Generated by Django 3.2.18 on 2023-04-26 13:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('diamm_data', '0009_auto_20230426_1300'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArchiveIdentifier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=512)),
                ('identifier_type', models.IntegerField(choices=[(1, 'RISM'), (2, 'VIAF'), (3, 'Wikidata'), (4, 'GND (Gemeinsame Normdatei)'), (5, 'MusicBrainz Artist'), (6, 'ORCID'), (7, 'Bibliothèque national de France'), (8, 'Library of Congress')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('archive', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='identifiers', to='diamm_data.archive')),
            ],
        ),
    ]