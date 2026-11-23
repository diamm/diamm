from types import SimpleNamespace

from django.template.loader import get_template
from django.test import SimpleTestCase, override_settings
from rest_framework.test import APIRequestFactory

from diamm.models import SourceURL
from diamm.serializers.website.source import SourceDetailSerializer
from diamm.tests.test_diva_7_migration import RelatedObjects


@override_settings(ROOT_URLCONF="diamm.urls", HOSTNAME="testserver")
class MultipleManifestTests(SimpleTestCase):
    def setUp(self):
        self.serializer = SourceDetailSerializer(
            context={"request": APIRequestFactory().get("/sources/1/")}
        )
        self.links = [
            SimpleNamespace(type=SourceURL.HOST, link="https://example.org/", link_text="Host"),
            SimpleNamespace(
                type=SourceURL.IIIF_MANIFEST,
                link="https://example.org/first",
                link_text="First volume",
            ),
            SimpleNamespace(
                type=SourceURL.IIIF_MANIFEST,
                link="https://example.org/second",
                link_text="Second volume",
            ),
        ]

    def source(self, public_images=False, links=None):
        return SimpleNamespace(
            pk=1,
            images_are_public=public_images,
            has_manifest_link=bool(links),
            links=RelatedObjects(*(links or [])),
        )

    def test_manifest_choices_preserve_url_order_and_labels(self):
        choices = self.serializer.get_manifests(self.source(links=self.links))
        self.assertEqual(
            choices,
            [
                {"url": "https://example.org/first", "label": "First volume"},
                {"url": "https://example.org/second", "label": "Second volume"},
            ],
        )

    def test_first_link_is_default_without_public_images(self):
        source = self.source(links=self.links)
        self.assertEqual(
            self.serializer.get_manifest_url(source), "https://example.org/first"
        )
        self.assertTrue(self.serializer.get_has_external_manifest(source))

    def test_own_images_take_precedence_over_linked_manifests(self):
        source = self.source(public_images=True, links=self.links)
        self.assertEqual(
            self.serializer.get_manifest_url(source),
            "http://testserver/sources/1/manifest/",
        )
        self.assertFalse(self.serializer.get_has_external_manifest(source))
        self.assertEqual(self.serializer.get_manifests(source), [])
        self.assertNotIn('id="manifest-selector"', self.render_images(
            self.serializer.get_manifests(source)
        ))

    def test_missing_link_text_falls_back_to_url(self):
        self.links[1].link_text = None
        choices = self.serializer.get_manifests(self.source(links=self.links))
        self.assertEqual(choices[0]["label"], choices[0]["url"])

    def test_generated_manifest_is_retained_without_manifest_links(self):
        source = self.source(public_images=True)
        self.assertEqual(
            self.serializer.get_manifest_url(source),
            "http://testserver/sources/1/manifest/",
        )
        self.assertEqual(self.serializer.get_manifests(source), [])
        self.assertFalse(self.serializer.get_has_external_manifest(source))
        self.assertIsNone(self.serializer.get_manifest_url(self.source()))

    def render_images(self, manifests):
        return get_template("website/source/images.jinja2").template.render(
            content={"manifest_url": "https://example.org/first", "manifests": manifests}
        )

    def test_selector_only_appears_for_multiple_manifests(self):
        choices = self.serializer.get_manifests(self.source(links=self.links))
        for count in (0, 1):
            self.assertNotIn('id="manifest-selector"', self.render_images(choices[:count]))
        html = self.render_images(choices)
        self.assertIn('id="manifest-selector"', html)
        self.assertIn('value="https://example.org/first" selected>First volume', html)
        self.assertIn('value="https://example.org/second">Second volume', html)

    def test_selector_escapes_link_text(self):
        self.links[1].link_text = "<script>alert(1)</script>"
        html = self.render_images(
            self.serializer.get_manifests(self.source(links=self.links))
        )
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>alert(1)</script>", html)
