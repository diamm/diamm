from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class NewsPage(Page):
    class Meta:
        app_label = "diamm_site"

    body = RichTextField()
    summary = models.CharField(max_length=255)

    template = "website/cms/news_page.jinja2"
    parent_page_types = ["diamm_site.NewsIndexPage"]


NewsPage.content_panels = [
    FieldPanel("title", classname="full title"),
    FieldPanel("summary"),
    FieldPanel("body", classname="full"),
]
