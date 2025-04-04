# Generated by Django 5.1.6 on 2025-02-25 11:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("diamm_data", "0022_source_external_manifest_externalpage_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="source",
            name="external_manifest",
        ),
        migrations.AlterField(
            model_name="item",
            name="external_pages",
            field=models.ManyToManyField(
                blank=True,
                help_text="Only use with an external IIIF manifest. Use the 'pages' field for all other sources.",
                related_name="external_items",
                to="diamm_data.externalpage",
            ),
        ),
        migrations.AlterField(
            model_name="sourceurl",
            name="link",
            field=models.URLField(max_length=1024),
        ),
    ]
