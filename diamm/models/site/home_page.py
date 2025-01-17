from wagtail.admin.panels import FieldPanel
from wagtail.blocks import StructBlock, TextBlock
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page


class HomePage(Page):
    class Meta:
        app_label = "diamm_site"

    carousel = StreamField(
        [
            (
                "carousel",
                StructBlock(
                    [("image", ImageChooserBlock()), ("caption", TextBlock())],
                    template="website/blocks/carousel.jinja2",
                ),
            )
        ],
        use_json_field=True,
    )

    brief_description = RichTextField()
    publications_intro = RichTextField(blank=True, null=True)

    template = "index.jinja2"
    subbpage_types = ["diamm_site.ContentPage", "diamm_site.NewsIndexPage"]


HomePage.content_panels = [
    FieldPanel("title"),
    FieldPanel("carousel"),
    FieldPanel("brief_description"),
    FieldPanel("publications_intro"),
]
