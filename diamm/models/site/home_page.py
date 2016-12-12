from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore import blocks
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel


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

    template = "index.jinja2"
    subbpage_types = ["diamm_site.ContentPage", "diamm_site.NewsIndexPage"]


HomePage.content_panels = [
    StreamFieldPanel('carousel'),
    FieldPanel('brief_description'),
]
