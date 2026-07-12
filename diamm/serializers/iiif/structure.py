import ypres
from rest_framework.reverse import reverse

from diamm.serializers.iiif.helpers import create_metadata_block, language_map


class StructureSerializer(ypres.DictSerializer):
    ctx = ypres.StaticField(
        value="http://iiif.io/api/presentation/3/context.json", label="@context"
    )
    id = ypres.MethodField()
    type = ypres.StaticField(value="Range")
    label = ypres.MethodField(required=False)
    rendering = ypres.MethodField()
    items = ypres.MethodField()
    metadata = ypres.MethodField()

    def get_label(self, obj: dict) -> dict | None:
        if "composition_s" not in obj:
            return None

        return language_map(obj["composition_s"])

    def get_items(self, obj: dict) -> list | None:
        if not obj.get("pages_ii"):
            return None

        members = []
        for p in obj["pages_ii"]:
            canvas_id = reverse(
                "source-canvas-detail",
                kwargs={"source_id": obj["source_i"], "page_id": p},
                request=self.context["request"],
            )
            members.append({"id": canvas_id, "type": "Canvas"})

        return members

    def get_rendering(self, obj: dict) -> None | list[dict]:
        if not obj.get("composition_i"):
            return None

        return [
            {
                "id": reverse(
                    "composition-detail",
                    kwargs={"pk": obj["composition_i"]},
                    request=self.context["request"],
                ),
                "type": "Text",
                "format": "text/html",
                "label": language_map(obj["composition_s"]),
            }
        ]

    def get_id(self, obj: dict) -> str:
        return reverse(
            "source-range-detail",
            kwargs={"source_id": obj["source_i"], "item_id": obj["pk"]},
            request=self.context["request"],
        )

    def get_metadata(self, obj):
        return create_metadata_block(obj)

    # def get_service(self, obj: dict) -> dict:
    #     return StructureServiceSerializer(
    #         obj, context={"request": self.context["request"]}
    #     ).data
