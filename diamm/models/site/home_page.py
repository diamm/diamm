from wagtail.core.models import Page
from wagtail.core.fields import StreamField
from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel


class HomePage(Page):
    class Meta:
        app_label = "diamm_site"

    carousel = StreamField([
        ('carousel', blocks.StructBlock([
            ('image', ImageChooserBlock()),
            ('caption', blocks.TextBlock())
        ], template="website/blocks/carousel.jinja2"))
    ])

    brief_description = RichTextField()
    publications_intro = RichTextField(blank=True, null=True)

    template = "index.jinja2"
    subbpage_types = ["diamm_site.ContentPage", "diamm_site.NewsIndexPage"]


HomePage.content_panels = [
    FieldPanel('title'),
    StreamFieldPanel('carousel'),
    FieldPanel('brief_description'),
    FieldPanel('publications_intro')
]
