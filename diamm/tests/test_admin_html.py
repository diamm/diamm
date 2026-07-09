from __future__ import annotations

from django.contrib import admin
from django.test import TestCase
from model_bakery import baker

from diamm.admin.data.source import ItemInline, PagesInline
from diamm.admin.helpers.html import admin_change_link, html_join
from diamm.models.data.source import Source


class AdminHtmlTests(TestCase):
    def test_change_link_rendering(self) -> None:
        page = baker.make("diamm_data.Page")
        inline = PagesInline(Source, admin.site)
        rendered = str(inline.link_id_field(page))
        self.assertIn(f">{page.pk}</a>", rendered)
        self.assertIn(f"/admin/diamm_data/page/{page.pk}/change/", rendered)

    def test_joined_multi_value_output_and_escaping(self) -> None:
        joined = str(html_join(["Alpha", "<script>alert(1)</script>"]))
        self.assertIn("Alpha", joined)
        self.assertIn("; <br />", joined)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", joined)

    def test_admin_class_escaping_for_unexpected_content(self) -> None:
        item = baker.make(
            "diamm_data.Item",
            composition=baker.make(
                "diamm_data.Composition", title="<script>alert(1)</script>"
            ),
        )
        inline = ItemInline(Source, admin.site)
        rendered = str(inline.get_composition(item))
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", rendered)
        self.assertNotIn("<script>alert(1)</script>", rendered)

    def test_admin_change_link_helper_escapes_labels(self) -> None:
        rendered = str(admin_change_link("/admin/example/", '<img src=x onerror="x">'))
        self.assertIn("&lt;img src=x onerror=&quot;x&quot;&gt;", rendered)
