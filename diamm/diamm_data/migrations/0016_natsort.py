# Generated by Django 5.1.5 on 2025-01-28 10:43
from django.contrib.postgres.operations import CreateCollation
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "diamm_data",
            "0015_alter_imagetype_options_image_height_image_width_and_more",
        ),
    ]

    operations = [CreateCollation("natsort", provider="icu", locale="en-u-kn-true")]
