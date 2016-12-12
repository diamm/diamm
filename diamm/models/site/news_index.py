from django.db import models
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel


class NewsIndexPage(Page):
    class Meta:
        app_label = "diamm_site"

    body = RichTextField()

    template = "diamm_site/news_index.jinja2"
    subbpage_types = ["diamm_site.NewsPage"]


NewsIndexPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('body', classname="full"),
]
