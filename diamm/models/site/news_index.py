from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class NewsIndexPage(Page):
    class Meta:
        app_label = "diamm_site"

    body = RichTextField()

    template = "website/cms/news_index.jinja2"
    subbpage_types = ["diamm_site.NewsPage"]


NewsIndexPage.content_panels = [
    FieldPanel("title", classname="full title"),
    FieldPanel("body", classname="full"),
]
