from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import ujson
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import TestCase, override_settings
from rest_framework.test import APIRequestFactory

from diamm.iiif_auth import AUTH_CONTEXT
from diamm.models.data.set import Set
from diamm.serializers.iiif.canvas import CanvasSerializer
from diamm.serializers.iiif.collection import SetCollectionSerializer
from diamm.serializers.iiif.helpers import PRESENTATION_CONTEXT
from diamm.serializers.iiif.image import ImageSerializer
from diamm.serializers.iiif.manifest import SourceManifestSerializer
from diamm.serializers.iiif.structure import StructureSerializer
from diamm.serializers.search.source import SourceSearchSerializer


def collect_v2_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {
                "@id",
                "@type",
                "sequences",
                "canvases",
                "images",
                "resource",
                "on",
            }:
                yield key
            yield from collect_v2_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from collect_v2_keys(child)


class FakeSolrManager:
    image_results: list[dict] = []
    structure_results: list[dict] = []
    alternate_image_results: list[dict] = []

    def __init__(self) -> None:
        self.results = []

    def search(self, *_args, **kwargs) -> None:
        filters = kwargs.get("fq", [])
        if any(
            str(filter_value).startswith("{!terms f=pk}") for filter_value in filters
        ):
            self.results = self.alternate_image_results
        elif "type:image" in filters:
            self.results = self.image_results
        elif "type:item" in filters:
            self.results = self.structure_results


class FakeSetSolrManager:
    result: dict | None = None
    filters: list[str] = []

    def search(self, *_args, **kwargs) -> None:
        type(self).filters = kwargs.get("fq", [])

    @property
    def hits(self) -> int:
        return int(self.result is not None)

    @property
    def first(self) -> dict | None:
        return self.result


@override_settings(
    ROOT_URLCONF="diamm.urls",
    HOSTNAME="testserver",
    IIIF={"THUMBNAIL_WIDTH": "250,"},
)
class PresentationV3SerializerTests(TestCase):
    def setUp(self) -> None:
        Site.objects.create(domain="testserver", name="Test site")
        self.request = APIRequestFactory().get("/sources/1/manifest/")
        FakeSolrManager.image_results = []
        FakeSolrManager.structure_results = []
        FakeSolrManager.alternate_image_results = []
        FakeSetSolrManager.result = None
        FakeSetSolrManager.filters = []
        self.image_doc = {
            "pk": 10,
            "page_i": 100,
            "source_i": 1,
            "numeration_s": "1r",
            "width_i": 4096,
            "height_i": 3072,
            "image_type_s": "Primary",
        }

    @patch("diamm.serializers.iiif.collection.SolrManager", FakeSetSolrManager)
    def test_set_collection_serializes_as_presentation_v3_collection(self) -> None:
        source_set = Set.objects.create(
            type=Set.PARTBOOKS,
            cluster_shelfmark="MS 1 (a-b)",
            description="A reconstructed group of partbooks.",
        )
        FakeSetSolrManager.result = {
            "sources_json": [
                {
                    "pk": 11,
                    "public": True,
                    "display_name": "GB-Lbl MS 1 (a)",
                },
                {
                    "pk": 12,
                    "public": False,
                    "display_name": "GB-Lbl MS 1 (private)",
                },
                {
                    "pk": 13,
                    "public": True,
                    "display_name": "GB-Lbl MS 1 (b)",
                },
            ]
        }
        request = APIRequestFactory().get(f"/sets/{source_set.pk}/collection/")

        data = SetCollectionSerializer(
            source_set, context={"request": request}
        ).serialized

        self.assertEqual(data["@context"], PRESENTATION_CONTEXT)
        self.assertEqual(
            data["id"], f"http://testserver/sets/{source_set.pk}/collection/"
        )
        self.assertEqual(data["type"], "Collection")
        self.assertEqual(data["label"], {"none": ["MS 1 (a-b)"]})
        self.assertEqual(
            data["summary"], {"none": ["A reconstructed group of partbooks."]}
        )
        self.assertEqual(
            data["metadata"],
            [
                {
                    "label": {"en": ["Set type"]},
                    "value": {"none": ["Partbooks"]},
                }
            ],
        )
        self.assertEqual(
            data["homepage"][0]["id"],
            f"http://testserver/sets/{source_set.pk}/",
        )
        self.assertEqual(data["provider"][0]["type"], "Agent")
        self.assertEqual(
            [item["id"] for item in data["items"]],
            [
                "http://testserver/sources/11/manifest/",
                "http://testserver/sources/13/manifest/",
            ],
        )
        self.assertEqual(
            [item["label"] for item in data["items"]],
            [
                {"none": ["GB-Lbl MS 1 (a)"]},
                {"none": ["GB-Lbl MS 1 (b)"]},
            ],
        )
        self.assertEqual(
            FakeSetSolrManager.filters, ["type:set", f"pk:{source_set.pk}"]
        )
        self.assertEqual(list(collect_v2_keys(data)), [])

    @patch("diamm.serializers.iiif.collection.SolrManager", FakeSetSolrManager)
    def test_partbook_collection_advertises_synchronization_service(self) -> None:
        source_set = Set.objects.create(
            type=Set.PARTBOOKS, cluster_shelfmark="Synchronized partbooks"
        )
        FakeSetSolrManager.result = {"sources_json": []}

        response = self.client.get(f"/sets/{source_set.pk}/collection/")
        payload = ujson.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            payload["service"],
            [
                {
                    "id": f"http://testserver/sets/{source_set.pk}/sync/",
                    "type": "SynchronizationService1",
                    "profile": "https://www.diamm.ac.uk/profiles/synchronization/1",
                    "format": "application/json",
                }
            ],
        )

    @patch("diamm.serializers.iiif.collection.SolrManager", FakeSetSolrManager)
    def test_set_collection_endpoint_is_json_ld_and_always_excludes_private_sources(
        self,
    ) -> None:
        source_set = Set.objects.create(type=Set.FRAGMENTS, cluster_shelfmark="MS 2")
        FakeSetSolrManager.result = {
            "sources_json": [
                {"pk": 21, "public": True, "display_name": "Public source"},
                {"pk": 22, "public": False, "display_name": "Private source"},
            ]
        }

        anonymous_response = self.client.get(f"/sets/{source_set.pk}/collection/")
        staff = get_user_model().objects.create_user(
            email="collection-staff@example.com",
            password=None,
        )
        staff.is_staff = True
        staff.save(update_fields=["is_staff"])
        self.client.force_login(staff)
        staff_response = self.client.get(f"/sets/{source_set.pk}/collection/")

        for endpoint_response in (anonymous_response, staff_response):
            self.assertEqual(endpoint_response.status_code, 200)
            self.assertEqual(
                endpoint_response["Content-Type"], "application/ld+json"
            )
            payload = ujson.loads(endpoint_response.content)
            self.assertNotIn("service", payload)
            self.assertEqual(
                payload["items"],
                [
                    {
                        "id": "http://testserver/sources/21/manifest/",
                        "type": "Manifest",
                        "label": {"none": ["Public source"]},
                    }
                ],
            )

    @patch("diamm.serializers.iiif.collection.SolrManager", FakeSetSolrManager)
    def test_set_collection_can_be_empty_and_uses_fallback_label(self) -> None:
        source_set = Set.objects.create(type=Set.PROJECT, cluster_shelfmark=None)
        FakeSetSolrManager.result = {"sources_json": []}

        response = self.client.get(f"/sets/{source_set.pk}/collection/")
        payload = ujson.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["label"], {"none": [f"Set {source_set.pk}"]})
        self.assertNotIn("summary", payload)
        self.assertEqual(payload["items"], [])
        self.assertNotIn("service", payload)

    def test_unknown_set_collection_returns_not_found(self) -> None:
        response = self.client.get("/sets/999999/collection/")

        self.assertEqual(response.status_code, 404)

    def test_canvas_serializes_as_presentation_v3_canvas(self) -> None:
        data = CanvasSerializer(
            self.image_doc, context={"request": self.request}
        ).serialized

        self.assertEqual(data["id"], "http://testserver/sources/1/canvas/100/")
        self.assertNotIn("@context", data)
        self.assertEqual(data["type"], "Canvas")
        self.assertEqual(data["label"], {"none": ["1r"]})
        self.assertEqual(data["width"], 4096)
        self.assertEqual(data["height"], 3072)
        self.assertEqual(data["items"][0]["type"], "AnnotationPage")
        self.assertEqual(data["items"][0]["items"][0]["type"], "Annotation")
        self.assertEqual(data["items"][0]["items"][0]["motivation"], "painting")
        self.assertEqual(data["items"][0]["items"][0]["target"], data["id"])
        self.assertEqual(list(collect_v2_keys(data)), [])

    @patch("diamm.views.website.source.SOLR_CLIENT.raw_search")
    def test_canvas_endpoint_resolves_primary_image_by_source_and_page(
        self, raw_search
    ) -> None:
        raw_search.return_value = SimpleNamespace(hits=1, docs=[self.image_doc])

        response = self.client.get("/sources/1/canvas/100/")

        self.assertEqual(response.status_code, 200)
        raw_search.assert_called_once_with(
            "*:*",
            fq=[
                "type:image",
                "source_i:1",
                "page_i:100",
                "image_type_i:1",
            ],
            rows=1,
        )
        data = response.json()
        self.assertEqual(data["id"], "http://testserver/sources/1/canvas/100/")
        self.assertEqual(
            data["items"][0]["items"][0]["body"]["id"],
            "http://testserver/images/10/full/full/0/default.jpg",
        )

    @patch("diamm.views.website.source.SOLR_CLIENT.raw_search")
    def test_canvas_endpoint_returns_404_when_page_has_no_primary_image(
        self, raw_search
    ) -> None:
        raw_search.return_value = SimpleNamespace(hits=0, docs=[])

        response = self.client.get("/sources/1/canvas/100/")

        self.assertEqual(response.status_code, 404)

    def test_image_annotation_body_references_image_api_2_service(self) -> None:
        data = ImageSerializer(
            self.image_doc,
            context={
                "request": self.request,
                "source_id": 1,
                "page_id": 100,
                "canvas_id": "http://testserver/sources/1/canvas/100/",
            },
        ).serialized

        body = data["body"]
        self.assertEqual(body["type"], "Image")
        self.assertEqual(
            body["id"],
            "http://testserver/images/10/full/full/0/default.jpg",
        )
        self.assertEqual(body["service"][0]["id"], "http://testserver/images/10/")
        self.assertEqual(body["service"][0]["type"], "ImageService2")
        auth_service = body["service"][1]
        self.assertEqual(auth_service["type"], "AuthProbeService2")
        self.assertNotIn("@context", auth_service)
        self.assertEqual(
            auth_service["id"],
            "http://testserver/iiif/auth/probe/"
            "?uri=http%3A%2F%2Ftestserver%2Fimages%2F10%2Ffull%2Ffull%2F0%2Fdefault.jpg",
        )
        external, active = auth_service["service"]
        self.assertEqual(
            [external["profile"], active["profile"]], ["external", "active"]
        )
        self.assertNotIn("id", external)
        for field in ("label", "heading", "note", "confirmLabel"):
            self.assertNotIn(field, external)
        self.assertEqual(
            external["service"][0]["type"],
            "AuthAccessTokenService2",
        )
        self.assertEqual(
            external["service"][1]["type"],
            "AuthLogoutService2",
        )
        self.assertEqual(list(collect_v2_keys(data)), [])

    def test_image_annotation_preserves_alternates_as_v3_choice(self) -> None:
        FakeSolrManager.alternate_image_results = [
            {
                "pk": 11,
                "width_i": 2048,
                "height_i": 1536,
                "image_type_s": "Alternate",
            }
        ]
        image_doc = {**self.image_doc, "alt_images_ii": [11]}

        with patch("diamm.serializers.iiif.image.SolrManager", FakeSolrManager):
            data = ImageSerializer(
                image_doc,
                context={
                    "request": self.request,
                    "source_id": 1,
                    "page_id": 100,
                    "canvas_id": "http://testserver/sources/1/canvas/100/",
                },
            ).serialized

        self.assertEqual(data["body"]["type"], "Choice")
        self.assertEqual(len(data["body"]["items"]), 2)
        primary = data["body"]["items"][0]
        alternate = data["body"]["items"][1]
        self.assertEqual(
            alternate["id"],
            "http://testserver/images/11/full/full/0/default.jpg",
        )
        self.assertEqual(primary["service"][1]["type"], "AuthProbeService2")
        self.assertIn("%2Fimages%2F10%2F", primary["service"][1]["id"])
        self.assertEqual(alternate["service"][1]["type"], "AuthProbeService2")
        self.assertIn("%2Fimages%2F11%2F", alternate["service"][1]["id"])
        self.assertEqual(list(collect_v2_keys(data)), [])

    def test_manifest_serializes_as_presentation_v3_manifest(self) -> None:
        FakeSolrManager.image_results = [self.image_doc]
        FakeSolrManager.structure_results = [
            {
                "pk": 20,
                "source_i": 1,
                "composition_i": 30,
                "composition_s": "Kyrie",
                "pages_ii": [100],
                "item_title_s": "Kyrie",
            }
        ]
        source_doc = {
            "pk": 1,
            "display_name_s": "Source A",
            "notes_txt": ["A concise description."],
            "name_s": "Source A",
            "shelfmark_s": "MS 1",
            "cover_image_url_sni": "cover",
            "cover_image_i": 10,
        }

        with patch("diamm.serializers.iiif.manifest.SolrManager", FakeSolrManager):
            data = SourceManifestSerializer(
                source_doc, context={"request": self.request}
            ).serialized

        self.assertEqual(data["@context"], [AUTH_CONTEXT, PRESENTATION_CONTEXT])
        self.assertEqual(data["id"], "http://testserver/sources/1/manifest/")
        self.assertEqual(data["type"], "Manifest")
        self.assertEqual(data["label"], {"none": ["Source A"]})
        self.assertEqual(data["behavior"], ["paged"])
        self.assertEqual(data["summary"], {"none": ["A concise description."]})
        self.assertEqual(data["items"][0]["type"], "Canvas")
        self.assertNotIn("@context", data["items"][0])
        painting_body = data["items"][0]["items"][0]["items"][0]["body"]
        self.assertEqual(painting_body["service"][0]["type"], "ImageService2")
        self.assertEqual(painting_body["service"][1]["type"], "AuthProbeService2")
        self.assertEqual(data["structures"][0]["type"], "Range")
        self.assertEqual(
            data["structures"][0]["items"][0]["id"], data["items"][0]["id"]
        )
        self.assertEqual(data["requiredStatement"]["label"], {"en": ["Attribution"]})
        self.assertEqual(
            data["requiredStatement"]["value"],
            {"none": ["Digital Image Archive of Medieval Music"]},
        )
        self.assertEqual(data["provider"][0]["type"], "Agent")
        self.assertEqual(data["thumbnail"][0]["type"], "Image")
        self.assertEqual(len(data["thumbnail"][0]["service"]), 1)
        self.assertEqual(data["thumbnail"][0]["service"][0]["type"], "ImageService2")
        self.assertEqual(list(collect_v2_keys(data)), [])

    def test_manifest_uses_archive_copyright_as_required_statement(self) -> None:
        with patch("diamm.serializers.iiif.manifest.SolrManager", FakeSolrManager):
            data = SourceManifestSerializer(
                {
                    "pk": 1,
                    "display_name_s": "Source A",
                    "archive_copyright_s": "Images © Example Library",
                },
                context={"request": self.request},
            ).serialized

        self.assertEqual(
            data["requiredStatement"],
            {
                "label": {"en": ["Attribution"]},
                "value": {"none": ["Images © Example Library"]},
            },
        )

    def test_source_index_document_includes_archive_copyright(self) -> None:
        data = SourceSearchSerializer(
            {
                "type": "source",
                "pk": 1,
                "archive_copyright": "Images © Example Library",
                "identifiers": [],
                "notations": [],
                "set_identifiers": [],
                "set_cluster_shelfmarks": [],
                "notes": [],
                "bibliography": [],
            }
        ).serialized

        self.assertEqual(data["archive_copyright_s"], "Images © Example Library")

    def test_source_index_document_includes_virtual_status(self) -> None:
        for is_virtual in (True, False):
            with self.subTest(is_virtual=is_virtual):
                data = SourceSearchSerializer(
                    {
                        "type": "source",
                        "pk": 1,
                        "is_virtual": is_virtual,
                        "identifiers": [],
                        "notations": [],
                        "set_identifiers": [],
                        "set_cluster_shelfmarks": [],
                        "notes": [],
                        "bibliography": [],
                    }
                ).serialized

                self.assertEqual(data["is_virtual_b"], is_virtual)

    def test_manifest_metadata_links_and_escapes_composers(self) -> None:
        source_doc = {
            "pk": 1,
            "display_name_s": "Source A",
            "composers_ssni": [
                "Josquin <des Prez>|12|True",
                "Anonymous & unknown||",
                "Du Fay|34|False",
            ],
        }

        with patch("diamm.serializers.iiif.manifest.SolrManager", FakeSolrManager):
            data = SourceManifestSerializer(
                source_doc, context={"request": self.request}
            ).serialized

        composers = next(
            entry
            for entry in data["metadata"]
            if entry["label"] == {"en": ["Composers"]}
        )
        self.assertEqual(
            composers["value"],
            {
                "none": [
                    '<span><a href="http://testserver/people/12/">'
                    "Josquin &lt;des Prez&gt;?</a>; Anonymous &amp; unknown; "
                    '<a href="http://testserver/people/34/">Du Fay</a></span>'
                ]
            },
        )

    def test_range_serializes_items_and_rendering_as_presentation_v3(self) -> None:
        data = StructureSerializer(
            {
                "pk": 20,
                "source_i": 1,
                "composition_i": 30,
                "composition_s": "Kyrie",
                "pages_ii": [10, 11],
                "item_title_s": "Kyrie",
            },
            context={"request": self.request},
        ).serialized

        self.assertEqual(data["id"], "http://testserver/sources/1/range/20/")
        self.assertEqual(data["type"], "Range")
        self.assertEqual(data["label"], {"none": ["[NN] | Kyrie"]})
        self.assertEqual(
            data["items"][0],
            {"id": "http://testserver/sources/1/canvas/10/", "type": "Canvas"},
        )
        self.assertEqual(data["rendering"][0]["type"], "Text")
        self.assertEqual(list(collect_v2_keys(data)), [])

    def test_range_metadata_passes_request_to_composer_links(self) -> None:
        data = StructureSerializer(
            {
                "pk": 20,
                "source_i": 1,
                "item_title_s": "Kyrie",
                "composers_ssni": ["Composer|56|False"],
            },
            context={"request": self.request},
        ).serialized

        composers = next(
            entry
            for entry in data["metadata"]
            if entry["label"] == {"en": ["Composers"]}
        )
        self.assertEqual(
            composers["value"],
            {
                "none": [
                    '<span><a href="http://testserver/people/56/">Composer</a></span>'
                ]
            },
        )
