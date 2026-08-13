from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, SimpleTestCase

from diamm.helpers.solr import (
    PageRangeOutOfBoundsException,
    SearchSolrRequest,
    SolrPaginator,
    SolrSearchResult,
    build_search_query_params,
    build_search_solr_request,
)
from diamm.helpers.solr.pagination import SolrResultSerializer
from diamm.views.website.search import SearchView


class SearchQueryParamsTests(SimpleTestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_blank_query_falls_back_to_match_all(self) -> None:
        request = self.factory.get("/search/")
        params = build_search_query_params(request)
        self.assertEqual(params.query, "*:*")

    def test_type_all_preserves_all_search_types(self) -> None:
        request = self.factory.get("/search/", {"q": "mass", "type": "all"})
        params = build_search_query_params(request)
        solr_request = build_search_solr_request(params, is_staff=False)
        self.assertIsInstance(solr_request.filters["{!tag=type}type"], list)

    def test_sources_with_images_adds_source_and_image_filters(self) -> None:
        request = self.factory.get("/search/", {"type": "sources_with_images"})
        params = build_search_query_params(request)
        solr_request = build_search_solr_request(params, is_staff=False)
        self.assertEqual(solr_request.filters["{!tag=type}type"], "source")
        self.assertTrue(solr_request.filters["{!tag=type}source_with_images_b"])

    def test_or_and_and_facets_stay_separate(self) -> None:
        request = self.factory.get(
            "/search/",
            {"cities": ["A", "B"], "genre": ["Mass", "Motet"]},
        )
        params = build_search_query_params(request)
        self.assertEqual(params.filters["city_s"], ['"A"', '"B"'])
        self.assertEqual(params.exclusive_filters["genres_ss"], ['"Mass"', '"Motet"'])

    def test_date_range_parsing(self) -> None:
        request = self.factory.get("/search/", {"date_range": "1200to1300"})
        params = build_search_query_params(request)
        self.assertEqual(params.filters["facet_date_range_ii"], "[1200 TO 1300]")

    def test_virtual_sources_filter_accepts_each_boolean_value(self) -> None:
        for value in ("true", "false"):
            with self.subTest(value=value):
                request = self.factory.get("/search/", {"virtual_sources": value})
                params = build_search_query_params(request)

                self.assertEqual(params.filters["is_virtual_b"], value)

    def test_virtual_sources_filter_is_omitted_by_default(self) -> None:
        params = build_search_query_params(self.factory.get("/search/"))

        self.assertNotIn("is_virtual_b", params.filters)

    def test_staff_visibility_filter_is_conditional(self) -> None:
        request = self.factory.get("/search/")
        params = build_search_query_params(request)
        staff_request = build_search_solr_request(params, is_staff=True)
        public_request = build_search_solr_request(params, is_staff=False)
        self.assertNotIn("public_b", staff_request.filters)
        self.assertTrue(public_request.filters["public_b"])

    def test_invalid_page_coerces_to_first_page(self) -> None:
        request = self.factory.get("/search/", {"page": "abc"})
        params = build_search_query_params(request)
        self.assertEqual(params.page, 1)

    def test_source_result_exposes_existing_external_manifest_flag(self) -> None:
        request = self.factory.get("/search/")
        result = SolrResultSerializer(
            {
                "type": "source",
                "pk": 117,
                "display_name_s": "Test source",
                "public_images_b": False,
                "is_virtual_b": True,
                "external_manifest_b": True,
            },
            context={"request": request},
        ).serialized

        self.assertFalse(result["public_images"])
        self.assertTrue(result["is_virtual"])
        self.assertTrue(result["has_external_manifest"])

    def test_set_result_exposes_total_book_count(self) -> None:
        request = self.factory.get("/search/")
        result = SolrResultSerializer(
            {
                "type": "set",
                "pk": 12,
                "cluster_shelfmark_s": "Example partbooks",
                "sources_ii": [20, 21, 22],
            },
            context={"request": request},
        ).serialized

        self.assertEqual(result["sources"], 3)

    def test_empty_set_result_exposes_zero_book_count(self) -> None:
        request = self.factory.get("/search/")
        result = SolrResultSerializer(
            {
                "type": "set",
                "pk": 12,
                "cluster_shelfmark_s": "Empty set",
            },
            context={"request": request},
        ).serialized

        self.assertEqual(result["sources"], 0)

    def test_person_result_exposes_variant_names(self) -> None:
        request = self.factory.get("/search/")
        result = SolrResultSerializer(
            {
                "type": "person",
                "pk": 12,
                "display_name_s": "John Doe",
                "variant_names_ss": ["Johannes Doe", "Jean Doe"],
            },
            context={"request": request},
        ).serialized

        self.assertEqual(result["variant_names"], ["Johannes Doe", "Jean Doe"])


class SearchViewTests(SimpleTestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()

    def test_out_of_range_page_falls_back_to_first_page(self) -> None:
        request = self.factory.get("/search/", {"page": "99"})
        request.user = AnonymousUser()

        class FakePage:
            def __init__(self, page_number: int) -> None:
                self.page_number = page_number

            def get_paginated_response(self) -> dict[str, dict[str, int]]:
                return {"pagination": {"current_page": self.page_number}}

        class FakePaginator:
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                pass

            def page(self, page_number: int) -> FakePage:
                if page_number != 1:
                    raise PageRangeOutOfBoundsException()
                return FakePage(1)

        with patch("diamm.views.website.search.SolrPaginator", FakePaginator):
            response = SearchView.as_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["pagination"]["current_page"], 1)


class SolrPaginatorTests(SimpleTestCase):
    def setUp(self) -> None:
        self.request = RequestFactory().get("/search/")
        self.solr_request = SearchSolrRequest(
            query="mass",
            filters={"public_b": True},
            exclusive_filters={},
            sorts="score desc",
            request_context={"facet": "true"},
        )

    @staticmethod
    def result(*, hits: int) -> SolrSearchResult:
        return SolrSearchResult(
            docs=[],
            hits=hits,
            facets={},
            raw_response={},
            grouped={},
        )

    def test_requested_page_is_fetched_once(self) -> None:
        client = MagicMock()
        client.search.return_value = self.result(hits=50)
        paginator = SolrPaginator(self.solr_request, self.request, client=client)

        page = paginator.page(2)

        self.assertEqual(page.number, 2)
        client.search.assert_called_once()
        self.assertEqual(client.search.call_args.kwargs["start"], paginator.page_size)

    def test_out_of_range_page_can_fall_back_to_first_page(self) -> None:
        client = MagicMock()
        client.search.side_effect = [self.result(hits=20), self.result(hits=20)]
        paginator = SolrPaginator(self.solr_request, self.request, client=client)

        with self.assertRaises(PageRangeOutOfBoundsException):
            paginator.page(99)
        page = paginator.page(1)

        self.assertEqual(page.number, 1)
        self.assertEqual(client.search.call_count, 2)
        self.assertEqual(client.search.call_args.kwargs["start"], 0)
