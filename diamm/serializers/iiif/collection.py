import ypres
from rest_framework.reverse import reverse

from diamm.helpers.solr import SolrManager
from diamm.serializers.iiif.helpers import (
    PRESENTATION_CONTEXT,
    diamm_provider,
    language_map,
)

SYNCHRONIZATION_PROFILE = "https://www.diamm.ac.uk/profiles/synchronization/1"


class SetCollectionSerializer(ypres.Serializer):
    ctx = ypres.StaticField(value=PRESENTATION_CONTEXT, label="@context")
    id = ypres.MethodField()
    type = ypres.StaticField(value="Collection")
    label = ypres.MethodField()
    summary = ypres.MethodField(required=False)
    metadata = ypres.MethodField()
    homepage = ypres.MethodField()
    provider = ypres.MethodField()
    service = ypres.MethodField(required=False)
    items = ypres.MethodField()

    def get_id(self, obj) -> str:
        return reverse(
            "set-collection", kwargs={"pk": obj.pk}, request=self.context["request"]
        )

    def get_label(self, obj) -> dict:
        return language_map(obj.cluster_shelfmark or f"Set {obj.pk}")

    def get_summary(self, obj) -> dict | None:
        if not obj.description:
            return None
        return language_map(obj.description)

    def get_metadata(self, obj) -> list[dict]:
        return [
            {
                "label": language_map("Set type", "en"),
                "value": language_map(obj.set_type),
            }
        ]

    def get_homepage(self, obj) -> list[dict]:
        return [
            {
                "id": reverse(
                    "set-detail",
                    kwargs={"pk": obj.pk},
                    request=self.context["request"],
                ),
                "type": "Text",
                "format": "text/html",
                "label": self.get_label(obj),
            }
        ]

    def get_provider(self, obj) -> list[dict]:
        del obj
        return diamm_provider()

    def get_service(self, obj) -> list[dict] | None:
        if obj.type != obj.PARTBOOKS:
            return None

        return [
            {
                "id": reverse(
                    "set-sync",
                    kwargs={"pk": obj.pk},
                    request=self.context["request"],
                ),
                "type": "SynchronizationService1",
                "profile": SYNCHRONIZATION_PROFILE,
                "format": "application/json",
            }
        ]

    def get_items(self, obj) -> list[dict]:
        connection = SolrManager()
        connection.search("*:*", fq=["type:set", f"pk:{obj.pk}"])

        if connection.hits == 0 or connection.first is None:
            return []

        items = []
        for source in connection.first.get("sources_json", []):
            if not source.get("public", False):
                continue

            items.append(
                {
                    "id": reverse(
                        "source-manifest",
                        kwargs={"pk": source["pk"]},
                        request=self.context["request"],
                    ),
                    "type": "Manifest",
                    "label": language_map(source["display_name"]),
                }
            )

        return items
