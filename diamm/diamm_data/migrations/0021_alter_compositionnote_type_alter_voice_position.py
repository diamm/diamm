# Generated by Django 5.1.6 on 2025-02-21 11:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("diamm_data", "0020_alter_source_options"),
    ]

    operations = [
        migrations.AlterField(
            model_name="compositionnote",
            name="type",
            field=models.IntegerField(
                choices=[
                    (1, "Alternate Title"),
                    (2, "Pars"),
                    (3, "General Note"),
                    (4, "Attribution Note"),
                    (5, "Contrafact Note"),
                    (6, "Intabulation Note"),
                ]
            ),
        ),
        migrations.AlterField(
            model_name="voice",
            name="position",
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
