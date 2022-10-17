from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core import blocks
from wagtail.core.fields import RichTextField
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from wagtail.images.blocks import ImageChooserBlock


class HomePage(Page):
    class Meta:
        app_label = "diamm_site"

    carousel = StreamField([
        ('carousel', blocks.StructBlock([
            ('image', ImageChooserBlock()),
            ('caption', blocks.TextBlock())
        ], template="website/blocks/carousel.jinja2"))
    ], use_json_field=False)

    brief_description = RichTextField()
    publications_intro = RichTextField(blank=True, null=True)

    template = "index.jinja2"
    subbpage_types = ["diamm_site.ContentPage", "diamm_site.NewsIndexPage"]


HomePage.content_panels = [
    FieldPanel('title'),
    FieldPanel('carousel'),
    FieldPanel('brief_description'),
    FieldPanel('publications_intro')
]
