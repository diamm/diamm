from django.db import models
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.core import fields
from wagtail.core.models import Page


class DissertationPage(Page):
    class Meta:
        app_label = "diamm_site"

    author = models.ForeignKey(
        "diamm_data.BibliographyAuthor",
        on_delete=models.PROTECT,
        related_name='+'
    )
    abstract = fields.RichTextField()
    university = models.CharField(max_length=255)
    year = models.IntegerField()
    degree = models.CharField(max_length=64)
    attachment = models.ForeignKey(
        'wagtaildocs.Document',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    template = "website/cms/dissertation_page.jinja2"

    parent_page_types = ['diamm_site.ContentPage']
    content_panels = Page.content_panels + [
        FieldPanel('author'),
        FieldPanel('abstract', classname="full"),
        FieldPanel('university'),
        FieldPanel('year'),
        FieldPanel('degree'),
        FieldPanel('attachment')
    ]
