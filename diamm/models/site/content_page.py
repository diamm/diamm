import os
from django.db import models
from django.conf import settings
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel


class ContentPage(Page):
    class Meta:
        app_label = "diamm_site"

    body = RichTextField()
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    tmpl = models.FilePathField("Template",
        path=os.path.join(settings.BASE_DIR, "diamm", "templates", "website", "cms", "content_page"),
        match=".*\.jinja2",
        max_length=255,
        blank=True,
        null=True
    )

    def get_template(self, request, *args, **kwargs):
        if self.tmpl:
            return os.path.relpath(self.tmpl, os.path.join(settings.BASE_DIR, 'diamm', 'templates'))
        return "website/cms/content_page.jinja2"


ContentPage.content_panels = [
    FieldPanel('title', classname="full title"),
    FieldPanel('body', classname="full"),
    ImageChooserPanel('cover_image'),
    FieldPanel('tmpl')
]
