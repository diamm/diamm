# Generated by Django 3.2.18 on 2023-04-25 12:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('diamm_data', '0007_archive_former_sigla'),
    ]

    operations = [
        migrations.AlterField(
            model_name='archivenote',
            name='type',
            field=models.IntegerField(choices=[(1, 'Private'), (2, 'Other Names'), (3, 'Comments')]),
        ),
        migrations.CreateModel(
            name='PersonIdentifier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=512)),
                ('identifier_type', models.IntegerField(choices=[(1, 'VIAF'), (2, 'Wikidata'), (3, 'GND (Gemeinsame Normdatei)'), (4, 'MusicBrainz Artist'), (5, 'ORCID'), (7, 'Bibliothèque national de France'), (8, 'Library of Congress')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='identifiers', to='diamm_data.person')),
            ],
        ),
        migrations.AddConstraint(
            model_name='personidentifier',
            constraint=models.UniqueConstraint(fields=('person', 'identifier_type'), name='person_identifier_type'),
        ),
    ]