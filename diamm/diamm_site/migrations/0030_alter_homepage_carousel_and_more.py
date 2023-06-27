# Generated by Django 4.2.2 on 2023-06-27 07:25

from django.db import migrations
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks


class Migration(migrations.Migration):
    dependencies = [
        ("diamm_site", "0029_auto_20221014_1258"),
    ]

    operations = [
        migrations.AlterField(
            model_name="homepage",
            name="carousel",
            field=wagtail.fields.StreamField(
                [
                    (
                        "carousel",
                        wagtail.blocks.StructBlock(
                            [
                                ("image", wagtail.images.blocks.ImageChooserBlock()),
                                ("caption", wagtail.blocks.TextBlock()),
                            ],
                            template="website/blocks/carousel.jinja2",
                        ),
                    )
                ],
                use_json_field=True,
            ),
        ),
        migrations.AlterField(
            model_name="publicationpage",
            name="pricing",
            field=wagtail.fields.StreamField(
                [
                    (
                        "price",
                        wagtail.blocks.StructBlock(
                            [
                                ("description", wagtail.blocks.CharBlock()),
                                ("price", wagtail.blocks.DecimalBlock()),
                                ("purchase_link", wagtail.blocks.URLBlock()),
                            ],
                            template="website/blocks/pricing_field.jinja2",
                        ),
                    )
                ],
                use_json_field=True,
            ),
        ),
    ]
