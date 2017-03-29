from django.db import models
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel


class PublicationPage(Page):
    class Meta:
        app_label = "diamm_site"

    body = RichTextField()
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
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
    ])
    # purchase_link = models.URLField(blank=True)
    show_on_front = models.BooleanField(default=False)
    teaser = models.CharField(max_length=255, blank=True, null=True)

    template = "website/cms/publication_page.jinja2"
    parent_page_types = ['diamm_site.ContentPage']

PublicationPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('body', classname="full"),
    ImageChooserPanel('cover_image'),
    StreamFieldPanel('pricing'),
    # FieldPanel('purchase_link'),
    FieldPanel('show_on_front'),
    FieldPanel('teaser'),
]
