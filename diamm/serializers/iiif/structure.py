import ypres
from rest_framework.reverse import reverse

from diamm.serializers.iiif.helpers import create_metadata_block, language_map


class StructureSerializer(ypres.DictSerializer):
    id = ypres.MethodField()
    type = ypres.StaticField(value="Range")
    label = ypres.MethodField(required=False)
    rendering = ypres.MethodField()
    items = ypres.MethodField()
    metadata = ypres.MethodField()

    def get_label(self, obj: dict) -> dict:
        title = obj.get("composition_s") or obj.get("item_title_s") or "[No title]"
        folio_start = obj.get("folio_start_s")
        folio_end = obj.get("folio_end_s")

        if folio_start and folio_end and folio_start != folio_end:
            folios = f"{folio_start}–{folio_end}"
        else:
            folios = folio_start or folio_end or "[NN]"

        label_parts = [folios, title]

        if composers := obj.get("composers_ss"):
            label_parts.append(f"({'; '.join(composers)})")

        return language_map(" | ".join(label_parts))

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
        return create_metadata_block(obj, self.context["request"])

    # def get_service(self, obj: dict) -> dict:
    #     return StructureServiceSerializer(
    #         obj, context={"request": self.context["request"]}
    #     ).data
