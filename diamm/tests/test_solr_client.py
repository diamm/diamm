from __future__ import annotations

from datetime import timedelta
from typing import Any
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.test import SimpleTestCase
from pyreqwest.exceptions import ConnectError, ConnectTimeoutError, StatusError

from diamm.helpers.solr import (
    SolrClient,
    SolrConnectionError,
    SolrResponseError,
    SolrTimeoutError,
)


class FakeResponse:
    def __init__(
        self,
        payload: dict[str, Any] | None = None,
        *,
        error: Exception | None = None,
    ) -> None:
        self.payload = payload or {}
        self.error = error

    def error_for_status(self) -> None:
        if self.error:
            raise self.error

    def bytes(self) -> bytes:
        return b"{}"

    def json(self) -> dict[str, Any]:
        return self.payload


class FakeRequest:
    def __init__(self, response: FakeResponse, capture: dict[str, Any]) -> None:
        self.response = response
        self.capture = capture

    def query(self, query: dict[str, Any]) -> FakeRequest:
        self.capture["query"] = query
        return self

    def headers(self, headers: dict[str, str]) -> FakeRequest:
        self.capture["headers"] = headers
        return self

    def body_json(self, body: Any) -> FakeRequest:
        self.capture["json"] = body
        return self

    def build(self) -> FakeRequest:
        return self

    def send(self) -> FakeResponse:
        return self.response


class FakeClient:
    def __init__(self, response: FakeResponse, capture: dict[str, Any]) -> None:
        self.response = response
        self.capture = capture

    def request(self, method: str, url: str) -> FakeRequest:
        self.capture["method"] = method
        self.capture["url"] = url
        return FakeRequest(self.response, self.capture)

    def close(self) -> None:
        self.capture["closed"] = True


class SolrClientTests(SimpleTestCase):
    def test_successful_search_index_and_commit(self) -> None:
        capture: dict[str, Any] = {}
        response = FakeResponse(
            {
                "response": {"docs": [{"id": "abc"}], "numFound": 1},
                "facet_counts": {"facet_fields": {}},
            }
        )
        client = SolrClient(base_server="http://solr.example/solr", live_core="diamm")

        with patch.object(
            client, "_build_http_client", return_value=FakeClient(response, capture)
        ):
            result = client.search(
                "*:*",
                filters={"type": "source"},
                exclusive_filters={},
                sorts="score desc",
                start=0,
                rows=20,
                request_context=None,
            )
        self.assertEqual(result.hits, 1)
        self.assertTrue(
            capture["url"].startswith("http://solr.example/solr/diamm/select?")
        )
        self.assertIn("fq=type%3Asource", capture["url"])

        capture = {}
        with patch.object(
            client,
            "_build_http_client",
            return_value=FakeClient(FakeResponse({"responseHeader": {"status": 0}}), capture),
        ):
            result = client.index([{"id": 1}], core="diamm_ingest")
        self.assertTrue(result)
        self.assertEqual(capture["json"], [{"id": 1}])

        capture = {}
        with patch.object(
            client,
            "_build_http_client",
            return_value=FakeClient(FakeResponse({"responseHeader": {"status": 0}}), capture),
        ):
            result = client.commit(core="diamm_ingest")
        self.assertTrue(result)
        self.assertEqual(capture["json"], {"commit": {}})

    def test_non_search_methods_treat_empty_response_as_success(self) -> None:
        capture: dict[str, Any] = {}
        client = SolrClient(base_server="http://solr.example/solr", live_core="diamm")

        with patch.object(
            client,
            "_build_http_client",
            return_value=FakeClient(FakeResponse({}), capture),
        ):
            result = client.reload_core(core="diamm")

        self.assertTrue(result)
        self.assertEqual(capture["query"], {"action": "RELOAD", "core": "diamm"})

    def test_delete_all_returns_true_for_successful_response(self) -> None:
        capture: dict[str, Any] = {}
        client = SolrClient(base_server="http://solr.example/solr", live_core="diamm")

        with patch.object(
            client,
            "_build_http_client",
            return_value=FakeClient(FakeResponse({"responseHeader": {"status": 0}}), capture),
        ):
            result = client.delete_all(core="diamm")

        self.assertTrue(result)
        self.assertEqual(capture["json"], {"delete": {"query": "*:*"}})

    def test_timeout_and_connection_errors_are_mapped(self) -> None:
        client = SolrClient()

        timeout_response = FakeResponse(
            error=ConnectTimeoutError("timeout", {"causes": None})
        )
        with patch.object(
            client,
            "_build_http_client",
            return_value=FakeClient(timeout_response, {}),
        ):
            with self.assertRaises(SolrTimeoutError):
                client.commit(core="diamm")

        connect_response = FakeResponse(error=ConnectError("offline", {"causes": None}))
        with patch.object(
            client,
            "_build_http_client",
            return_value=FakeClient(connect_response, {}),
        ):
            with self.assertRaises(SolrConnectionError):
                client.commit(core="diamm")

    def test_non_2xx_status_is_mapped(self) -> None:
        client = SolrClient()
        error = StatusError("bad status", {"status": 500, "causes": None})
        with patch.object(
            client,
            "_build_http_client",
            return_value=FakeClient(FakeResponse(error=error), {}),
        ):
            with self.assertRaises(SolrResponseError) as exc:
                client.commit(core="diamm")
        self.assertEqual(exc.exception.status_code, 500)

    def test_empty_query_list_values_are_dropped_before_building_request(self) -> None:
        capture: dict[str, Any] = {}
        response = FakeResponse({"response": {"docs": [], "numFound": 0}})
        client = SolrClient(base_server="http://solr.example/solr", live_core="diamm")

        with patch.object(
            client, "_build_http_client", return_value=FakeClient(response, capture)
        ):
            client.search(
                "*:*",
                filters={},
                exclusive_filters={},
                sorts=None,
                start=0,
                rows=20,
                request_context={"facet.pivot": [], "facet.field": ["type"]},
            )

        self.assertNotIn("facet.pivot", capture["url"])
        self.assertIn("facet.field=type", capture["url"])

    def test_raw_search_uses_settings_page_size_when_rows_omitted(self) -> None:
        capture: dict[str, Any] = {}
        response = FakeResponse({"response": {"docs": [], "numFound": 0}})
        client = SolrClient(base_server="http://solr.example/solr", live_core="diamm")

        with patch.object(
            client, "_build_http_client", return_value=FakeClient(response, capture)
        ):
            client.raw_search("*:*")

        self.assertEqual(capture["query"]["rows"], settings.SOLR["PAGE_SIZE"])

    def test_raw_search_explicit_rows_overrides_settings_page_size(self) -> None:
        capture: dict[str, Any] = {}
        response = FakeResponse({"response": {"docs": [], "numFound": 0}})
        client = SolrClient(base_server="http://solr.example/solr", live_core="diamm")

        with patch.object(
            client, "_build_http_client", return_value=FakeClient(response, capture)
        ):
            client.raw_search("*:*", rows=7)

        self.assertEqual(capture["query"]["rows"], 7)

    def test_tls_verification_remains_enabled_by_default(self) -> None:
        builder = MagicMock()
        builder.connect_timeout.return_value = builder
        builder.read_timeout.return_value = builder
        builder.build.return_value = MagicMock()
        with patch(
            "diamm.helpers.solr.client.SyncClientBuilder", return_value=builder
        ):
            client = SolrClient(
                connect_timeout=timedelta(seconds=1),
                read_timeout=timedelta(seconds=2),
            )
            client._build_http_client()
        builder.danger_accept_invalid_certs.assert_not_called()
