import json
import re
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.sites.models import Site
from django.template.loader import get_template
from django.test import SimpleTestCase, TestCase, override_settings
from jinja2.runtime import new_context
from rest_framework.test import APIRequestFactory

from diamm.models import (
    Archive,
    Composition,
    CompositionURL,
    CustomUserModel,
    Item,
    Source,
    SourceNote,
)
from diamm.serializers.search.composer_inventory import (
    ComposerInventorySearchSerializer,
)
from diamm.serializers.website.source import (
    SourceComposerInventoryCompositionSerializer,
    SourceDetailSerializer,
    SourceInventorySerializer,
)


class RelatedObjects:
    def __init__(self, *objects):
        self.objects = objects

    def all(self):
        return self.objects


class EmptySolrManager:
    def __init__(self):
        self.docs = []
        self.hits = 0
        self.results = []

    def search(self, *args, **kwargs):
        return None


class SourceSummaryTests(TestCase):
    def setUp(self):
        archive = Archive.objects.create(name="British Library", siglum="GB-Lbl")
        self.source = Source.objects.create(
            archive=archive,
            shelfmark="Royal 1 A I",
            date_statement="c. 1400",
        )
        SourceNote.objects.create(
            source=self.source,
            type=SourceNote.GENERAL_NOTE,
            note='A "quoted" description.',
        )
        SourceNote.objects.create(
            source=self.source,
            type=SourceNote.EXTENT_NOTE,
            note="This is not part of the summary.",
        )

    def test_source_detail_serializer_exposes_display_summary(self):
        self.assertIn("display_summary", SourceDetailSerializer._field_map)

    def test_source_detail_defers_inventory_serialization(self):
        self.assertIn("has_inventory", SourceDetailSerializer._field_map)
        self.assertNotIn("inventory", SourceDetailSerializer._field_map)
        self.assertNotIn("composer_inventory", SourceDetailSerializer._field_map)
        self.assertNotIn("uninventoried", SourceDetailSerializer._field_map)

    def test_display_summary_loads_notes_once(self):
        source = Source.objects.select_related("archive").get(pk=self.source.pk)

        with self.assertNumQueries(1):
            summary = source.display_summary

        self.assertEqual(
            summary,
            'GB-Lbl Royal 1 A I; c. 1400; A "quoted" description.',
        )

    def test_display_summary_uses_prefetched_notes(self):
        source = (
            Source.objects.select_related("archive")
            .prefetch_related("notes")
            .get(pk=self.source.pk)
        )

        with self.assertNumQueries(0):
            summary = source.display_summary

        self.assertEqual(
            summary,
            'GB-Lbl Royal 1 A I; c. 1400; A "quoted" description.',
        )


@override_settings(ROOT_URLCONF="diamm.urls", HOSTNAME="testserver")
class SourceInventoryPanelTests(TestCase):
    def setUp(self):
        Site.objects.create(domain="testserver", name="Test site")
        archive = Archive.objects.create(name="British Library", siglum="GB-Lbl")
        self.public_source = Source.objects.create(
            archive=archive,
            shelfmark="Royal 1 A I",
            public=True,
        )
        self.private_source = Source.objects.create(
            archive=archive,
            shelfmark="Private source",
            public=False,
        )

    @patch(
        "diamm.serializers.website.source.SolrManager",
        EmptySolrManager,
    )
    def test_public_inventory_fragment_is_available_anonymously(self):
        response = self.client.get(
            f"/sources/{self.public_source.pk}/inventory/",
            HTTP_ACCEPT="text/html",
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<html")

    @patch(
        "diamm.serializers.website.source.SolrManager",
        EmptySolrManager,
    )
    def test_inventory_item_displays_composition_external_links(self):
        composition = Composition.objects.create(title="Kyrie")
        Item.objects.create(source=self.public_source, composition=composition)
        CompositionURL.objects.create(
            composition=composition,
            type=1,
            link="https://example.test/edition/kyrie",
            link_text="Modern edition of the Kyrie",
        )

        response = self.client.get(
            f"/sources/{self.public_source.pk}/inventory/",
            HTTP_ACCEPT="text/html",
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "External editions and scores")
        self.assertContains(response, "Modern edition of the Kyrie")
        self.assertContains(response, "https://example.test/edition/kyrie")

    def test_private_inventory_fragment_is_hidden_anonymously(self):
        response = self.client.get(
            f"/sources/{self.private_source.pk}/inventory/",
            HTTP_ACCEPT="text/html",
        )

        self.assertEqual(response.status_code, 404)

    @patch(
        "diamm.serializers.website.source.SolrManager",
        EmptySolrManager,
    )
    def test_private_inventory_fragment_is_available_to_staff(self):
        user = CustomUserModel.objects.create_user(
            email="editor@example.org",
            password=None,
            is_staff=True,
        )
        self.client.force_login(user)

        response = self.client.get(
            f"/sources/{self.private_source.pk}/inventory/",
            HTTP_ACCEPT="text/html",
        )

        self.assertEqual(response.status_code, 200)


@override_settings(ROOT_URLCONF="diamm.urls", HOSTNAME="testserver")
class InventoryImageViewerSerializerTests(SimpleTestCase):
    def setUp(self):
        self.request = APIRequestFactory().get("/sources/1/")

    def item(self, *pages):
        return SimpleNamespace(
            pk=100,
            source_id=1,
            pages=RelatedObjects(*pages),
            num_voices=None,
            folio_start="2r",
            folio_end=None,
            composition=None,
            composition_id=None,
            item_title="Untitled item",
            bibliography_json=None,
            voices=RelatedObjects(),
            notes=RelatedObjects(),
            source_attribution=None,
            fragment=False,
            item_completeness=None,
        )

    def serialize(self, item):
        return SourceInventorySerializer(
            item, context={"request": self.request}
        ).serialized

    def test_internal_page_uses_canonical_canvas_id(self):
        page = SimpleNamespace(
            pk=11,
            sort_order=1,
            external=False,
            iiif_canvas_uri=None,
        )

        data = self.serialize(self.item(page))

        self.assertEqual(
            data["image_viewer_url"],
            "#/images?p=canvas%3Ahttp%3A%2F%2Ftestserver%2Fsources%2F1%2Fcanvas%2F11%2F",
        )

    def test_first_page_is_selected_by_sort_order_then_id(self):
        later = SimpleNamespace(
            pk=30, sort_order=5, external=False, iiif_canvas_uri=None
        )
        tied_high_id = SimpleNamespace(
            pk=20, sort_order=1, external=False, iiif_canvas_uri=None
        )
        tied_low_id = SimpleNamespace(
            pk=10, sort_order=1, external=False, iiif_canvas_uri=None
        )

        data = self.serialize(self.item(later, tied_high_id, tied_low_id))

        self.assertIn("%2Fcanvas%2F10%2F", data["image_viewer_url"])

    def test_external_page_uses_manifest_canvas_uri(self):
        page = SimpleNamespace(
            pk=11,
            sort_order=1,
            external=True,
            iiif_canvas_uri="https://example.org/iiif/canvas/a?view=1",
        )

        data = self.serialize(self.item(page))

        self.assertEqual(
            data["image_viewer_url"],
            "#/images?p=canvas%3Ahttps%3A%2F%2Fexample.org%2Fiiif%2Fcanvas%2Fa%3Fview%3D1",
        )

    def test_missing_page_or_external_canvas_omits_link(self):
        self.assertNotIn("image_viewer_url", self.serialize(self.item()))
        page = SimpleNamespace(pk=11, sort_order=1, external=True, iiif_canvas_uri=None)
        self.assertNotIn("image_viewer_url", self.serialize(self.item(page)))

    def test_composer_inventory_page_data_produces_external_target(self):
        data = SourceComposerInventoryCompositionSerializer(
            {
                "id": 7,
                "title": "Kyrie",
                "source_id": 1,
                "page_id": 11,
                "page_external": True,
                "page_canvas_uri": "https://example.org/canvas/11",
            },
            context={"request": self.request},
        ).serialized

        self.assertEqual(
            data["image_viewer_url"],
            "#/images?p=canvas%3Ahttps%3A%2F%2Fexample.org%2Fcanvas%2F11",
        )

    def test_composer_search_document_retains_indexed_page_data(self):
        composition = {
            "id": 7,
            "title": "Kyrie",
            "source_id": 1,
            "page_id": 11,
            "page_external": False,
        }
        data = ComposerInventorySearchSerializer(
            {
                "record_type": "composerinventory",
                "pk": 10,
                "person_id": None,
                "source_id": 1,
                "items": [100],
                "compositions": [composition],
            }
        ).serialized

        self.assertEqual(data["compositions_json"][0]["page_id"], 11)
        self.assertFalse(data["compositions_json"][0]["page_external"])


class DivaTemplateTests(SimpleTestCase):
    def test_source_detail_serializes_json_ld_safely(self):
        template = get_template("website/source/source_detail.jinja2").template
        name = 'Royal "Choir" </script><script>alert(1)</script> 🎼'
        summary = 'First line\n"Second" & <third>'
        absolute_url = 'https://example.org/sources/1/?q="quoted"&x=<tag>'
        context = new_context(
            template.environment,
            template.name,
            template.blocks,
            {
                "content": {
                    "display_name": name,
                    "display_summary": summary,
                    "inventory": [],
                    "uninventoried": [],
                    "manifest_url": None,
                    "sets": [],
                    "bibliography": [],
                    "contributions": [],
                },
                "request": SimpleNamespace(
                    build_absolute_uri=lambda: absolute_url,
                    user=SimpleNamespace(is_authenticated=False),
                ),
            },
        )

        head = "".join(template.blocks["head"](context))
        match = re.search(
            r'<script type="application/ld\+json">(.*?)</script>',
            head,
            re.DOTALL,
        )

        self.assertIsNotNone(match)
        structured_data = json.loads(match.group(1))
        self.assertEqual(structured_data["url"], absolute_url)
        self.assertEqual(structured_data["name"], name)
        self.assertEqual(structured_data["description"], summary)
        self.assertNotIn("</script><script>", match.group(1))

    def test_source_detail_uses_one_page_scoped_alpine_component(self):
        source_detail = Path(
            "diamm/templates/website/source/source_detail.jinja2"
        ).read_text()
        related_templates = "\n".join(
            (
                source_detail,
                Path("diamm/templates/website/source/inventory.jinja2").read_text(),
                Path("diamm/templates/website/macros.jinja2").read_text(),
            )
        )

        self.assertIn("Alpine.data('sourceDetail'", source_detail)
        self.assertIn('x-data="sourceDetail"', source_detail)
        self.assertIn("selectSourceTab", source_detail)
        self.assertIn("selectInventoryTab", source_detail)
        self.assertNotIn("Alpine.store", related_templates)
        self.assertNotIn("$store.sourceTabs", related_templates)
        self.assertNotIn("$store.inventoryTabs", related_templates)

    def test_source_detail_syncs_tabs_with_hash_navigation(self):
        source_detail = Path(
            "diamm/templates/website/source/source_detail.jinja2"
        ).read_text()

        self.assertIn("const tabsFromHash = () =>", source_detail)
        self.assertIn("this.syncTabsFromHash();", source_detail)
        self.assertIn(
            'window.addEventListener("hashchange", this.hashChangeHandler)',
            source_detail,
        )
        self.assertIn(
            'window.removeEventListener("hashchange", this.hashChangeHandler)',
            source_detail,
        )
        self.assertIn("this.selectedSourceTab = tabs.selectedSourceTab", source_detail)
        self.assertIn(
            "this.selectedInventoryTab = tabs.selectedInventoryTab",
            source_detail,
        )

    def test_source_detail_loads_inventory_fragment_once(self):
        source_detail = Path(
            "diamm/templates/website/source/source_detail.jinja2"
        ).read_text()

        self.assertIn("data-inventory-url=\"{{ url('source-inventory'", source_detail)
        self.assertIn(
            "if (this.inventoryLoaded || this.inventoryLoading)", source_detail
        )
        self.assertIn("this.inventoryHtml = await response.text()", source_detail)
        self.assertIn('x-html="inventoryHtml"', source_detail)
        self.assertIn("inventoryError", source_detail)
        self.assertIn("loadInventory()", source_detail)

    def test_images_template_defers_viewer_dependencies(self):
        template = get_template("website/source/images.jinja2")
        html = template.template.render(
            content={
                "has_external_manifest": False,
                "manifest_url": "https://example.org/manifest",
                "archive": {"copyright": None},
            }
        )

        self.assertIn("source-image-viewer.js", html)
        self.assertIn('data-manifest-url="https://example.org/manifest"', html)
        self.assertIn('data-openseadragon-url="https://cdn.jsdelivr.net/', html)
        self.assertIn('data-diva-url="/static/vendor/diva-7.4.0/diva.js"', html)
        self.assertNotIn(
            '<script src="https://cdn.jsdelivr.net/npm/openseadragon', html
        )
        self.assertNotIn('<script src="/static/vendor/diva-7.4.0/diva.js"', html)
        self.assertNotIn("diva-page-details", html)
        self.assertNotIn("createStructureDataLookup", html)
        self.assertNotIn("diva.css", html)

    def test_integration_uses_diva_7_configuration_and_navigation(self):
        script = Path("diamm/static/apps/source-image-viewer.js").read_text()

        self.assertIn('sidebarPanel: "contents"', script)
        self.assertIn("showSidebar: true", script)
        self.assertIn("showTitle: false", script)
        self.assertIn("initialPage: initialPageForTarget(initialTarget)", script)
        self.assertIn('{ by: "canvasId", value: canvasId }', script)
        self.assertIn('{ by: "label", value: target }', script)
        self.assertIn("return canvasId ?", script)
        self.assertIn("goToTarget(viewer, initialTarget)", script)
        self.assertIn("instance.goToPage(pageIndex)", script)
        self.assertIn('document.createElement("script")', script)
        self.assertIn("wrapper.dataset.openseadragonUrl", script)
        self.assertIn("wrapper.dataset.divaUrl", script)
        self.assertLess(
            script.index("wrapper.dataset.openseadragonUrl"),
            script.index("wrapper.dataset.divaUrl"),
        )
        self.assertIn("if (viewerPromise)", script)
        self.assertNotIn("window.fetch =", script)
        self.assertNotIn("__diammProbeFetchInstalled", script)
        self.assertNotIn("Diva.Events", script)
        self.assertNotIn("gotoPageByLabel", script)

    def render_inventory(self, authenticated, external):
        template = get_template("website/source/inventory-composition-order.jinja2")
        entry = {
            "composition": "Kyrie",
            "url": "/compositions/7/",
            "folio_start": "2r",
            "folio_end": None,
            "fragment": False,
            "completeness": None,
            "composers": None,
            "image_viewer_url": "#/images?p=canvas%3Ahttps%3A%2F%2Fexample.org%2Fcanvas%2F11",
        }
        return template.template.render(
            content={
                "manifest_url": "https://example.org/manifest",
                "has_external_manifest": external,
                "inventory": [entry],
            },
            request=SimpleNamespace(
                user=SimpleNamespace(is_authenticated=authenticated)
            ),
        )

    def test_authenticated_internal_inventory_has_accessible_fragment_link(self):
        html = self.render_inventory(authenticated=True, external=False)

        self.assertIn('href="#/images?p=canvas%3Ahttps', html)
        self.assertIn('aria-label="View images for 2r"', html)
        self.assertNotIn("history.pushState", html)
        self.assertNotIn("<button", html)

    def test_anonymous_external_inventory_has_fragment_link(self):
        html = self.render_inventory(authenticated=False, external=True)
        self.assertIn('href="#/images?p=canvas%3Ahttps', html)

    def test_anonymous_internal_inventory_hides_fragment_link(self):
        html = self.render_inventory(authenticated=False, external=False)
        self.assertNotIn('href="#/images?p=', html)
