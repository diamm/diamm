# Generated by Django 5.1.6 on 2025-02-28 10:20

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("diamm_data", "0025_alter_sourcenote_type"),
    ]

    operations = [
        migrations.DeleteModel(
            name="SourceManifest",
        ),
    ]
