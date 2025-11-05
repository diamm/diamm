from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class DissertationPage(Page):
    class Meta:
        app_label = "diamm_site"
        ordering = ("author__last_name", "year")

    author = models.ForeignKey(
        "diamm_data.BibliographyAuthor", on_delete=models.PROTECT, related_name="+"
    )
    abstract = RichTextField()
    university = models.CharField(max_length=255)
    year = models.IntegerField()
    degree = models.CharField(max_length=64)
    attachment = models.ForeignKey(
        "wagtaildocs.Document",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    template = "website/cms/dissertation_page.jinja2"

    parent_page_types = ["diamm_site.ContentPage"]
    content_panels = Page.content_panels + [
        FieldPanel("author"),
        FieldPanel("abstract", classname="full"),
        FieldPanel("university"),
        FieldPanel("year"),
        FieldPanel("degree"),
        FieldPanel("attachment"),
    ]
