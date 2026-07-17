import json
import re
from pathlib import Path
from types import SimpleNamespace

from django.template.loader import get_template
from django.test import SimpleTestCase, override_settings
from jinja2.runtime import new_context
from rest_framework.test import APIRequestFactory

from diamm.serializers.search.composer_inventory import (
    ComposerInventorySearchSerializer,
)
from diamm.serializers.website.source import (
    SourceComposerInventoryCompositionSerializer,
    SourceInventorySerializer,
)


class RelatedObjects:
    def __init__(self, *objects):
        self.objects = objects

    def all(self):
        return self.objects


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
        page = SimpleNamespace(
            pk=11, sort_order=1, external=True, iiif_canvas_uri=None
        )
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
                Path(
                    "diamm/templates/website/source/inventory.jinja2"
                ).read_text(),
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
        self.assertIn(
            "this.selectedSourceTab = tabs.selectedSourceTab", source_detail
        )
        self.assertIn(
            "this.selectedInventoryTab = tabs.selectedInventoryTab",
            source_detail,
        )

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
        self.assertNotIn('<script src="https://cdn.jsdelivr.net/npm/openseadragon', html)
        self.assertNotIn('<script src="/static/vendor/diva-7.4.0/diva.js"', html)
        self.assertNotIn("diva-page-details", html)
        self.assertNotIn("createStructureDataLookup", html)
        self.assertNotIn("diva.css", html)

    def test_integration_uses_diva_7_configuration_and_navigation(self):
        script = Path("diamm/static/apps/source-image-viewer.js").read_text()

        self.assertIn('sidebarPanel: "contents"', script)
        self.assertIn("showSidebar: true", script)
        self.assertIn("showTitle: false", script)
        self.assertIn("initialPage: initialPage", script)
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
        template = get_template(
            "website/source/inventory-composition-order.jinja2"
        )
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
