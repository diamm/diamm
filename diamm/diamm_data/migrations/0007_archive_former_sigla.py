# Generated by Django 3.2.18 on 2023-04-19 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diamm_data', '0006_auto_20221014_1312'),
    ]

    operations = [
        migrations.AddField(
            model_name='archive',
            name='former_sigla',
            field=models.CharField(blank=True, help_text='Separated by comma', max_length=255, null=True),
        ),
    ]
