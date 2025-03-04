# Generated by Django 5.1.6 on 2025-02-25 14:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "diamm_data",
            "0022_source_external_manifest_externalpage_and_more_squashed_0024_alter_sourceurl_type",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="sourcenote",
            name="type",
            field=models.IntegerField(
                choices=[
                    (1, "General Description"),
                    (97, "RISM Description"),
                    (98, "Census Catalogue of Music Description"),
                    (4, "Extent"),
                    (5, "Physical Description"),
                    (6, "Binding"),
                    (7, "Ownership"),
                    (8, "Watermark"),
                    (9, "Liminary Note"),
                    (10, "Notation"),
                    (11, "Date"),
                    (12, "Dedication"),
                    (13, "Ruling"),
                    (14, "Foliation"),
                    (15, "Decoration"),
                    (16, "Index"),
                    (17, "Surface"),
                    (18, "DIAMM Note"),
                    (99, "Private Note"),
                    (19, "Inventory"),
                ]
            ),
        ),
    ]
