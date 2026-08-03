from unittest.mock import patch

import ujson
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import TestCase, override_settings

from diamm.models.data.set import Set


class FakeSyncSolrManager:
    set_document: dict | None = None
    image_documents: list[dict] = []
    item_documents: list[dict] = []
    searches: list[dict] = []

    def __init__(self) -> None:
        self.docs = []

    def search(self, query: str, **kwargs) -> None:
        filters = kwargs.get("fq", [])
        type(self).searches.append({"query": query, **kwargs})
        if "type:set" in filters:
            self.docs = [self.set_document] if self.set_document is not None else []
        elif "type:image" in filters:
            self.docs = self.image_documents
        elif "type:item" in filters:
            self.docs = self.item_documents

    @property
    def first(self) -> dict | None:
        return self.docs[0] if self.docs else None

    @property
    def results(self):
        yield from self.docs


@override_settings(ROOT_URLCONF="diamm.urls", HOSTNAME="testserver")
class SetSyncTests(TestCase):
    def setUp(self) -> None:
        Site.objects.create(domain="testserver", name="Test site")
        self.source_set = Set.objects.create(
            type=Set.PARTBOOKS, cluster_shelfmark="Test partbooks"
        )
        FakeSyncSolrManager.set_document = None
        FakeSyncSolrManager.image_documents = []
        FakeSyncSolrManager.item_documents = []
        FakeSyncSolrManager.searches = []

    @patch("diamm.serializers.set_sync.SolrManager", FakeSyncSolrManager)
    def test_sync_response_builds_forward_and_reverse_lookup_indexes(self) -> None:
        FakeSyncSolrManager.set_document = {
            "sources_json": [
                {"pk": 12, "public": True, "display_name": "Second source"},
                {"pk": 99, "public": False, "display_name": "Private source"},
                {"pk": 11, "public": True, "display_name": "First source"},
            ]
        }
        FakeSyncSolrManager.image_documents = [
            {"source_i": 11, "page_i": 101},
            {"source_i": 11, "page_i": 102},
            {"source_i": 12, "page_i": 201},
            {"source_i": 12, "page_i": 202},
            # A second primary image must not duplicate its Page's Canvas.
            {"source_i": 12, "page_i": 202},
        ]
        # Deliberately return Source 11 first: the Set's Source order must win.
        FakeSyncSolrManager.item_documents = [
            {
                "pk": 1101,
                "source_i": 11,
                "composition_i": 501,
                "composition_s": "Shared composition",
                "pages_ii": [101, 999],
            },
            {
                "pk": 1201,
                "source_i": 12,
                "composition_i": 502,
                "composition_s": "Singleton composition",
                "pages_ii": [202],
            },
            {
                "pk": 1202,
                "source_i": 12,
                "composition_i": 501,
                "composition_s": "Shared composition",
                "pages_ii": [201, 201],
            },
            {
                "pk": 1203,
                "source_i": 12,
                "composition_i": 501,
                "composition_s": "Shared composition",
                # Item index order differs from manifest order.
                "pages_ii": [202, 201],
            },
        ]

        response = self.client.get(f"/sets/{self.source_set.pk}/sync/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        data = ujson.loads(response.content)
        source_11 = "http://testserver/sources/11/"
        source_12 = "http://testserver/sources/12/"
        composition_501 = "http://testserver/compositions/501/"
        composition_502 = "http://testserver/compositions/502/"
        range_1101 = "http://testserver/sources/11/range/1101/"
        range_1201 = "http://testserver/sources/12/range/1201/"
        range_1202 = "http://testserver/sources/12/range/1202/"
        range_1203 = "http://testserver/sources/12/range/1203/"
        canvas_101 = "http://testserver/sources/11/canvas/101/"
        canvas_201 = "http://testserver/sources/12/canvas/201/"
        canvas_202 = "http://testserver/sources/12/canvas/202/"

        self.assertEqual(data["version"], 1)
        self.assertEqual(
            data["set"], f"http://testserver/sets/{self.source_set.pk}/"
        )
        self.assertNotIn("sourceOrder", data)
        self.assertEqual(list(data["sources"]), [source_12, source_11])
        self.assertNotIn("ranges", data["sources"][source_12])
        self.assertEqual(
            data["sources"][source_12],
            {
                "label": "Second source",
                "manifest": "http://testserver/sources/12/manifest/",
            },
        )
        self.assertNotIn("http://testserver/sources/99/", data["sources"])
        self.assertEqual(
            data["compositionOrder"], [composition_502, composition_501]
        )
        self.assertEqual(
            data["compositions"][composition_501]["ranges"],
            [range_1202, range_1203, range_1101],
        )
        self.assertEqual(
            data["compositions"][composition_502]["ranges"], [range_1201]
        )
        self.assertEqual(
            data["ranges"][range_1101]["canvases"], [canvas_101]
        )
        self.assertEqual(
            data["ranges"][range_1202],
            {
                "source": source_12,
                "composition": composition_501,
                "canvases": [canvas_201],
            },
        )
        self.assertEqual(
            data["ranges"][range_1203]["canvases"], [canvas_201, canvas_202]
        )
        self.assertEqual(
            data["canvases"][canvas_202], [range_1201, range_1203]
        )
        self.assertEqual(len(FakeSyncSolrManager.searches), 3)

        image_search = FakeSyncSolrManager.searches[1]
        item_search = FakeSyncSolrManager.searches[2]
        self.assertIn("{!terms f=source_i}12,11", image_search["fq"])
        self.assertIn("image_type_i:1", image_search["fq"])
        self.assertIn("composition_i:[* TO *]", item_search["fq"])
        self.assertIn("pages_ii:[* TO *]", item_search["fq"])

    @patch("diamm.serializers.set_sync.SolrManager", FakeSyncSolrManager)
    def test_sync_is_public_only_for_anonymous_and_staff_users(self) -> None:
        FakeSyncSolrManager.set_document = {
            "sources_json": [
                {"pk": 21, "public": True, "display_name": "Public"},
                {"pk": 22, "public": False, "display_name": "Private"},
            ]
        }
        FakeSyncSolrManager.image_documents = [{"source_i": 21, "page_i": 210}]
        FakeSyncSolrManager.item_documents = [
            {
                "pk": 211,
                "source_i": 21,
                "composition_i": 701,
                "composition_s": "Public work",
                "pages_ii": [210],
            }
        ]

        anonymous = ujson.loads(
            self.client.get(f"/sets/{self.source_set.pk}/sync/").content
        )
        staff = get_user_model().objects.create_user(
            email="sync-staff@example.com", password=None, is_staff=True
        )
        self.client.force_login(staff)
        staff_response = ujson.loads(
            self.client.get(f"/sets/{self.source_set.pk}/sync/").content
        )

        self.assertEqual(anonymous, staff_response)
        self.assertEqual(
            list(anonymous["sources"]), ["http://testserver/sources/21/"]
        )
        for search in FakeSyncSolrManager.searches:
            if "type:image" in search.get("fq", []) or "type:item" in search.get(
                "fq", []
            ):
                self.assertIn("{!terms f=source_i}21", search["fq"])

    @patch("diamm.serializers.set_sync.SolrManager", FakeSyncSolrManager)
    def test_sync_can_return_an_empty_index(self) -> None:
        FakeSyncSolrManager.set_document = {"sources_json": []}

        response = self.client.get(f"/sets/{self.source_set.pk}/sync/")
        data = ujson.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["compositionOrder"], [])
        self.assertEqual(data["sources"], {})
        self.assertEqual(data["compositions"], {})
        self.assertEqual(data["ranges"], {})
        self.assertEqual(data["canvases"], {})
        self.assertEqual(len(FakeSyncSolrManager.searches), 1)

    def test_unknown_set_sync_returns_not_found(self) -> None:
        response = self.client.get("/sets/999999/sync/")

        self.assertEqual(response.status_code, 404)
