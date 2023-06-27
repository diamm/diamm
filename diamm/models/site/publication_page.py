from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.blocks import StructBlock, CharBlock, DecimalBlock, URLBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page


class PublicationPage(Page):
    class Meta:
        app_label = "diamm_site"

    body = RichTextField()
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    pricing = StreamField([
        ('price', StructBlock([
            ('description', CharBlock()),
            ('price', DecimalBlock()),
            ('purchase_link', URLBlock())
        ], template="website/blocks/pricing_field.jinja2")),
    ], use_json_field=True)
    # purchase_link = models.URLField(blank=True)
    show_on_front = models.BooleanField(default=False)
    teaser = models.CharField(max_length=255, blank=True, null=True)

    template = "website/cms/publication_page.jinja2"
    parent_page_types = ['diamm_site.ContentPage']


PublicationPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('body', classname="full"),
    FieldPanel('cover_image'),
    FieldPanel('pricing'),
    # FieldPanel('purchase_link'),
    FieldPanel('show_on_front'),
    FieldPanel('teaser'),
]
