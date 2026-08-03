from collections import defaultdict

from rest_framework import serializers
from rest_framework.reverse import reverse

from diamm.helpers.solr import SolrManager


class SetSyncSerializer(serializers.BaseSerializer):
    """Build the lookup indexes used to synchronize a Set's source viewers."""

    def to_representation(self, obj) -> dict:
        request = self.context["request"]
        set_url = reverse("set-detail", kwargs={"pk": obj.pk}, request=request)

        set_connection = SolrManager()
        set_connection.search(
            "*:*",
            fq=["type:set", f"pk:{obj.pk}"],
            fl="sources_json",
        )
        set_document = set_connection.first or {}

        source_records = []
        seen_source_ids = set()
        for source in set_document.get("sources_json", []):
            if not source or not source.get("public", False):
                continue

            source_id = int(source["pk"])

            if source_id in seen_source_ids:
                continue

            seen_source_ids.add(source_id)
            source_records.append((source_id, source))

        response = {
            "version": 1,
            "set": set_url,
            "compositionOrder": [],
            "sources": {},
            "compositions": {},
            "ranges": {},
            "canvases": {},
        }
        if not source_records:
            return response

        source_ids = [source_id for source_id, _source in source_records]
        source_filter = "{!terms f=source_i}" + ",".join(map(str, source_ids))

        canvas_pages_by_source = self._get_canvas_pages(source_filter)
        items_by_source = self._get_items(source_filter)

        for source_id, source in source_records:
            source_url = reverse(
                "source-detail", kwargs={"pk": source_id}, request=request
            )
            response["sources"][source_url] = {
                "label": source.get("display_name") or f"Source {source_id}",
                "manifest": reverse(
                    "source-manifest", kwargs={"pk": source_id}, request=request
                ),
            }

            available_pages = canvas_pages_by_source.get(source_id, [])
            for item in items_by_source.get(source_id, []):
                page_ids = self._matching_page_ids(item, available_pages)
                if not page_ids:
                    continue

                composition_id = int(item["composition_i"])
                range_url = reverse(
                    "source-range-detail",
                    kwargs={"source_id": source_id, "item_id": item["pk"]},
                    request=request,
                )
                composition_url = reverse(
                    "composition-detail",
                    kwargs={"pk": composition_id},
                    request=request,
                )
                canvas_urls = [
                    reverse(
                        "source-canvas-detail",
                        kwargs={"source_id": source_id, "page_id": page_id},
                        request=request,
                    )
                    for page_id in page_ids
                ]

                if composition_url not in response["compositions"]:
                    response["compositionOrder"].append(composition_url)
                    response["compositions"][composition_url] = {
                        "label": item.get("composition_s") or "[No title]",
                        "ranges": [],
                    }

                response["compositions"][composition_url]["ranges"].append(range_url)
                response["ranges"][range_url] = {
                    "source": source_url,
                    "composition": composition_url,
                    "canvases": canvas_urls,
                }
                for canvas_url in canvas_urls:
                    response["canvases"].setdefault(canvas_url, []).append(range_url)

        return response

    @staticmethod
    def _get_canvas_pages(source_filter: str) -> dict[int, list[int]]:
        connection = SolrManager()
        connection.search(
            "*:*",
            fq=["type:image", source_filter, "image_type_i:1"],
            fl="source_i,page_i",
            sort="source_i asc, sort_order_f asc, numeration_ans asc, page_i asc",
        )

        pages_by_source = defaultdict(list)
        seen_pages_by_source = defaultdict(set)
        for image in connection.results:
            source_id = int(image["source_i"])
            page_id = int(image["page_i"])

            if page_id in seen_pages_by_source[source_id]:
                continue

            seen_pages_by_source[source_id].add(page_id)
            pages_by_source[source_id].append(page_id)
        return pages_by_source

    @staticmethod
    def _get_items(source_filter: str) -> dict[int, list[dict]]:
        connection = SolrManager()
        connection.search(
            "*:*",
            fq=[
                "type:item",
                source_filter,
                "composition_i:[* TO *]",
                "pages_ii:[* TO *]",
            ],
            fl="pk,source_i,composition_i,composition_s,pages_ii",
            sort="source_i asc, source_order_f asc, folio_start_ans asc, pk asc",
        )

        items_by_source = defaultdict(list)
        for item in connection.results:
            items_by_source[int(item["source_i"])].append(item)
        return items_by_source

    @staticmethod
    def _matching_page_ids(item: dict, available_pages: list[int]) -> list[int]:
        item_page_ids = {int(page_id) for page_id in item.get("pages_ii", [])}
        return [page_id for page_id in available_pages if page_id in item_page_ids]
