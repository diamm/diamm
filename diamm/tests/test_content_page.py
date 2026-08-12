from django.template.loader import get_template
from django.test import TestCase

from diamm.models.site.content_page import ContentPage


class ContentPageTemplateTests(TestCase):
    def test_legacy_absolute_template_path_is_portable(self) -> None:
        page = ContentPage(
            tmpl=(
                "../../../../../www.diamm.ac.uk/webapps/diamm/diamm/templates/"
                "website/cms/content_page/publications.jinja2"
            )
        )

        template_name = page.get_template(None)

        self.assertEqual(template_name, "website/cms/content_page/publications.jinja2")
        self.assertIsNotNone(get_template(template_name))
