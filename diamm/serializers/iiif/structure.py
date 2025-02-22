import serpy
from rest_framework.reverse import reverse

from diamm.serializers.fields import StaticField
from diamm.serializers.iiif.helpers import create_metadata_block
from diamm.serializers.serializers import ContextDictSerializer


class StructureSerializer(ContextDictSerializer):
    id = serpy.MethodField(label="@id")
    type = StaticField(label="@type", value="sc:Range")
    label = serpy.StrField(attr="composition_s", required=False)
    rendering = serpy.MethodField()
    canvases = serpy.MethodField()
    metadata = serpy.MethodField()

    def get_canvases(self, obj: dict) -> list | None:
        if not obj.get("pages_ii"):
            return None

        members = []
        for p in obj["pages_ii"]:
            canvas_id = reverse(
                "source-canvas-detail",
                kwargs={"source_id": obj["source_i"], "page_id": p},
                request=self.context["request"],
            )
            members.append(canvas_id)

        return members

    def get_rendering(self, obj: dict) -> None | dict:
        if not obj.get("composition_i"):
            return None

        return {
            "@id": reverse(
                "composition-detail",
                kwargs={"pk": obj["composition_i"]},
                request=self.context["request"],
            ),
            "format": "text/html",
            "label": obj["composition_s"],
        }

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
