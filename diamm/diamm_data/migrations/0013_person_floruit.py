# Generated by Django 4.2.2 on 2023-06-30 09:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("diamm_data", "0012_alter_sourceauthority_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="person",
            name="floruit",
            field=models.CharField(
                blank=True,
                help_text="Enter floruit dates only if no dates of birth or death are known. Do not enter both. Do not enter the 'fl.' prefix.",
                max_length=64,
                null=True,
            ),
        ),
    ]
