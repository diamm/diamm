from dataclasses import dataclass
from datetime import timedelta
from typing import Any
from urllib.parse import urlencode

from django.conf import settings
from pyreqwest.client import SyncClient, SyncClientBuilder
from pyreqwest.exceptions import (
    ConnectError,
    ConnectTimeoutError,
    PyreqwestError,
    ReadTimeoutError,
    RequestTimeoutError,
    StatusError,
)


class SolrError(Exception):
    pass


class SolrTimeoutError(SolrError):
    pass


class SolrConnectionError(SolrError):
    pass


class SolrResponseError(SolrError):
    def __init__(self, message: str, *, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


@dataclass
class SolrSearchResult:
    docs: list[dict[str, Any]]
    hits: int
    facets: dict[str, Any]
    raw_response: dict[str, Any]
    grouped: dict[str, Any]
    nextCursorMark: str | None = None


class SolrClient:
    def __init__(
        self,
        *,
        base_server: str | None = None,
        live_core: str | None = None,
        connect_timeout: timedelta | None = None,
        read_timeout: timedelta | None = None,
    ) -> None:
        self.base_server = (base_server or settings.SOLR["BASE_SERVER"]).rstrip("/")
        self.live_core = live_core or settings.SOLR["LIVE_CORE"]
        self.connect_timeout = connect_timeout or timedelta(seconds=2)
        self.read_timeout = read_timeout or timedelta(seconds=30)

    def search(
        self,
        query: str,
        *,
        filters: dict[str, Any] | None,
        exclusive_filters: dict[str, Any] | None,
        sorts: str | list[str] | None,
        start: int,
        rows: int,
        request_context: dict[str, Any] | None,
        raw_filters: list[str] | None = None,
    ) -> SolrSearchResult:
        params: dict[str, Any] = dict(request_context or {})
        core = params.pop("__core__", None)
        params["q"] = query
        params["start"] = start
        params["rows"] = rows
        if sorts:
            params["sort"] = ", ".join(sorts) if isinstance(sorts, list) else sorts

        fq: list[str] = self._build_filter_queries(
            filters or {}, exclusive_filters or {}
        )
        fq.extend(raw_filters or [])
        if fq:
            params["fq"] = fq

        data = self._request_json("GET", f"{self._core_url(core)}/select", query=params)
        response = data.get("response", {})
        return SolrSearchResult(
            docs=response.get("docs", []),
            hits=response.get("numFound", 0),
            facets=data.get("facet_counts", {}),
            raw_response=data,
            grouped=data.get("grouped", {}),
            nextCursorMark=data.get("nextCursorMark"),
        )

    def raw_search(
        self, query: str, *, core: str | None = None, **params: Any
    ) -> SolrSearchResult:
        rows = params.pop("rows", settings.SOLR["PAGE_SIZE"])
        start = params.pop("start", 0)
        sorts = params.pop("sort", None)
        structured_fq, raw_filters = self._partition_filter_queries(
            params.pop("fq", None)
        )
        filters, exclusive_filters = self._split_filter_queries(structured_fq)
        return self.search(
            query,
            filters=filters,
            exclusive_filters=exclusive_filters,
            sorts=sorts,
            start=start,
            rows=rows,
            request_context={**params, "__core__": core} if core else params,
            raw_filters=raw_filters,
        )

    def index(self, records: list[dict[str, Any]], *, core: str) -> bool:
        result = self._request_json(
            "POST",
            f"{self._core_url(core)}/update",
            json_body=records,
            headers={"Content-Type": "application/json"},
        )
        return self._request_succeeded(result)

    def delete_all(self, *, core: str) -> bool:
        result = self._request_json(
            "POST",
            f"{self._core_url(core)}/update",
            json_body={"delete": {"query": "*:*"}},
            headers={"Content-Type": "application/json"},
        )
        return self._request_succeeded(result)

    def delete(
        self, *, query: str | None = None, doc_id: str | None = None, core: str
    ) -> bool:
        payload: dict[str, Any]
        if doc_id is not None:
            payload = {"delete": {"id": doc_id}}
        elif query is not None:
            payload = {"delete": {"query": query}}
        else:
            raise ValueError("Either query or doc_id is required.")

        result = self._request_json(
            "POST",
            f"{self._core_url(core)}/update",
            json_body=payload,
            headers={"Content-Type": "application/json"},
        )
        return self._request_succeeded(result)

    def commit(self, *, core: str) -> bool:
        result = self._request_json(
            "POST",
            f"{self._core_url(core)}/update",
            json_body={"commit": {}},
            headers={"Content-Type": "application/json"},
        )
        return self._request_succeeded(result)

    def swap_cores(self, *, indexing_core: str, live_core: str) -> bool:
        result = self._request_json(
            "GET",
            f"{self.base_server}/admin/cores",
            query={"action": "SWAP", "core": indexing_core, "other": live_core},
        )
        return self._request_succeeded(result)

    def reload_core(self, *, core: str) -> bool:
        result = self._request_json(
            "GET",
            f"{self.base_server}/admin/cores",
            query={"action": "RELOAD", "core": core},
        )
        return self._request_succeeded(result)

    def _request_json(
        self,
        method: str,
        url: str,
        *,
        query: dict[str, Any] | None = None,
        json_body: Any = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        client = self._build_http_client()
        try:
            builder = client.request(method, url)
            if query:
                query = self._normalize_query_params(query)
                query.pop("__core__", None)
                if self._query_requires_manual_encoding(query):
                    builder = client.request(
                        method,
                        f"{url}?{urlencode(query, doseq=True)}",
                    )
                else:
                    builder = builder.query(query)
            if headers:
                builder = builder.headers(headers)
            if json_body is not None:
                builder = builder.body_json(json_body)
            response = builder.build().send()
            response.error_for_status()
            return response.json() if response.bytes() else {}
        except (ConnectTimeoutError, ReadTimeoutError, RequestTimeoutError) as exc:
            raise SolrTimeoutError(str(exc)) from exc
        except ConnectError as exc:
            raise SolrConnectionError(str(exc)) from exc
        except StatusError as exc:
            status_code = exc.details.get("status")
            raise SolrResponseError(str(exc), status_code=status_code) from exc
        except PyreqwestError as exc:
            raise SolrConnectionError(str(exc)) from exc
        finally:
            client.close()

    def _build_http_client(self) -> SyncClient:
        return (
            SyncClientBuilder()
            .connect_timeout(self.connect_timeout)
            .read_timeout(self.read_timeout)
            .build()
        )

    def _core_url(self, core: str | None = None) -> str:
        return f"{self.base_server}/{core or self.live_core}"

    @staticmethod
    def _request_succeeded(result: dict[str, Any]) -> bool:
        if not result:
            return True

        response_header = result.get("responseHeader")
        if isinstance(response_header, dict) and "status" in response_header:
            return response_header["status"] == 0

        return True

    @staticmethod
    def _normalize_query_params(query: dict[str, Any]) -> dict[str, Any]:
        normalized: dict[str, Any] = {}
        for key, value in dict(query).items():
            if value is None:
                continue
            if isinstance(value, (list, tuple)):
                filtered = [item for item in value if item is not None and item != ""]
                if not filtered:
                    continue
                normalized[key] = filtered
                continue
            normalized[key] = value
        return normalized

    @staticmethod
    def _query_requires_manual_encoding(query: dict[str, Any]) -> bool:
        return any(isinstance(value, (list, tuple)) for value in query.values())

    @staticmethod
    def _build_filter_queries(
        filters: dict[str, Any], exclusive_filters: dict[str, Any]
    ) -> list[str]:
        fqlist = []
        for key, value in filters.items():
            if isinstance(value, list):
                fqlist.append(" OR ".join([f"{key}:{field}" for field in value]))
            else:
                fqlist.append(f"{key}:{value}")

        for key, value in exclusive_filters.items():
            if isinstance(value, list):
                fqlist.append(" AND ".join([f"{key}:{field}" for field in value]))
            else:
                fqlist.append(f"{key}:{value}")

        return fqlist

    @staticmethod
    def _split_filter_queries(
        fq: list[str] | tuple[str, ...] | str | None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        if fq is None:
            return {}, {}

        clauses = [fq] if isinstance(fq, str) else list(fq)
        filters: dict[str, Any] = {}
        exclusive_filters: dict[str, Any] = {}
        for clause in clauses:
            target = exclusive_filters if " AND " in clause else filters
            if " OR " in clause:
                parts = clause.split(" OR ")
                key, _ = parts[0].split(":", 1)
                target[key] = [part.split(":", 1)[1] for part in parts]
            elif " AND " in clause:
                parts = clause.split(" AND ")
                key, _ = parts[0].split(":", 1)
                target[key] = [part.split(":", 1)[1] for part in parts]
            else:
                key, value = clause.split(":", 1)
                target[key] = value
        return filters, exclusive_filters

    @staticmethod
    def _partition_filter_queries(
        fq: list[str] | tuple[str, ...] | str | None,
    ) -> tuple[list[str], list[str]]:
        if fq is None:
            return [], []

        clauses = [fq] if isinstance(fq, str) else list(fq)
        structured: list[str] = []
        raw: list[str] = []
        for clause in clauses:
            if clause.startswith("{!") or ":" not in clause:
                raw.append(clause)
            else:
                structured.append(clause)
        return structured, raw


DEFAULT_SOLR_CLIENT = SolrClient()
