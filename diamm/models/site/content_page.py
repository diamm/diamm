from django.db import models
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import FieldPanel


class ContentPage(Page):
    class Meta:
        app_label = "diamm_site"

    body = RichTextField()

    template = "diamm_site/content_page.jinja2"

ContentPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('body', classname="full"),
]
