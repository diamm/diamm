# Generated by Django 5.1.6 on 2025-03-09 22:56

import django.db.models.functions.text
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("diamm_data", "0026_delete_sourcemanifest"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="genre",
            options={"ordering": (django.db.models.functions.text.Lower("name"),)},
        ),
    ]
