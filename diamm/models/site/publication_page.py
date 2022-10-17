from django.db import models
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core import blocks
from wagtail.core.fields import RichTextField
from wagtail.core.fields import StreamField
from wagtail.core.models import Page


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
        ('price', blocks.StructBlock([
            ('description', blocks.CharBlock()),
            ('price', blocks.DecimalBlock()),
            ('purchase_link', blocks.URLBlock())
        ], template="website/blocks/pricing_field.jinja2")),
    ], use_json_field=False)
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
