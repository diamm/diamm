from __future__ import annotations

from typing import Any
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, SimpleTestCase
from unittest.mock import patch

from diamm.helpers.solr_pagination import PageRangeOutOfBoundsException
from diamm.search import build_search_query_params, build_search_solr_request
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
