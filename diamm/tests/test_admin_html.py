from __future__ import annotations

from django.test import TestCase

from diamm.admin.helpers.html import admin_change_link, html_join


class AdminHtmlTests(TestCase):
    def test_joined_multi_value_output_and_escaping(self) -> None:
        joined = str(html_join(["Alpha", "<script>alert(1)</script>"]))
        self.assertIn("Alpha", joined)
        self.assertIn("; <br />", joined)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", joined)

    def test_admin_change_link_helper_escapes_labels(self) -> None:
        rendered = str(admin_change_link("/admin/example/", '<img src=x onerror="x">'))
        self.assertIn("&lt;img src=x onerror=&quot;x&quot;&gt;", rendered)
