# Generated by Django 5.1.5 on 2025-02-06 14:39

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("diamm_data", "0018_alter_image_location"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="image",
            name="iiif_response_cache",
        ),
    ]
