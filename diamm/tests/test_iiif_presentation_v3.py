from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework.test import APIRequestFactory

from diamm.iiif_auth import AUTH_CONTEXT
from diamm.serializers.iiif.canvas import CanvasSerializer
from diamm.serializers.iiif.helpers import PRESENTATION_CONTEXT
from diamm.serializers.iiif.image import ImageSerializer
from diamm.serializers.iiif.manifest import SourceManifestSerializer
from diamm.serializers.iiif.structure import StructureSerializer


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


@override_settings(
    ROOT_URLCONF="diamm.urls",
    HOSTNAME="testserver",
    IIIF={"THUMBNAIL_WIDTH": "250,"},
)
class PresentationV3SerializerTests(TestCase):
    def setUp(self) -> None:
        self.request = APIRequestFactory().get("/sources/1/manifest/")
        FakeSolrManager.image_results = []
        FakeSolrManager.structure_results = []
        FakeSolrManager.alternate_image_results = []
        self.image_doc = {
            "pk": 10,
            "source_i": 1,
            "numeration_s": "1r",
            "width_i": 4096,
            "height_i": 3072,
            "image_type_s": "Primary",
        }

    def test_canvas_serializes_as_presentation_v3_canvas(self) -> None:
        data = CanvasSerializer(
            self.image_doc, context={"request": self.request}
        ).serialized

        self.assertEqual(data["id"], "http://testserver/sources/1/canvas/10/")
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

    def test_image_annotation_body_references_image_api_2_service(self) -> None:
        data = ImageSerializer(
            self.image_doc,
            context={
                "request": self.request,
                "source_id": 1,
                "page_id": 10,
                "canvas_id": "http://testserver/sources/1/canvas/10/",
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
        self.assertEqual([external["profile"], active["profile"]], ["external", "active"])
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
                    "page_id": 10,
                    "canvas_id": "http://testserver/sources/1/canvas/10/",
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
                "pages_ii": [10],
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
        self.assertEqual(data["summary"], {"none": ["A concise description."]})
        self.assertEqual(data["items"][0]["type"], "Canvas")
        self.assertNotIn("@context", data["items"][0])
        painting_body = data["items"][0]["items"][0]["items"][0]["body"]
        self.assertEqual(painting_body["service"][0]["type"], "ImageService2")
        self.assertEqual(painting_body["service"][1]["type"], "AuthProbeService2")
        self.assertEqual(data["structures"][0]["type"], "Range")
        self.assertEqual(data["requiredStatement"]["label"], {"en": ["Attribution"]})
        self.assertEqual(data["provider"][0]["type"], "Agent")
        self.assertEqual(data["thumbnail"][0]["type"], "Image")
        self.assertEqual(len(data["thumbnail"][0]["service"]), 1)
        self.assertEqual(data["thumbnail"][0]["service"][0]["type"], "ImageService2")
        self.assertEqual(list(collect_v2_keys(data)), [])

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
