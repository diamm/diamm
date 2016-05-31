import serpy
from rest_framework.reverse import reverse
from diamm.serializers.serializers import ContextDictSerializer
from diamm.serializers.fields import StaticField
from diamm.serializers.iiif.service import ServiceSerializer



class StructureSerializer(ContextDictSerializer):
    canvases = serpy.MethodField()
    id = serpy.MethodField(
        label="@id"
    )
    type = StaticField(
        label="@type",
        value="sc:Range"
    )
    label = serpy.StrField(
        attr='composition_s'
    )

    service = serpy.MethodField()

    def get_canvases(self, obj):
        if not obj.get('pages_ii'):
            return []

        canvases = []
        for p in obj['pages_ii']:
            canvas_id = reverse("source-canvas-detail",
                                kwargs={"source_id": obj['source_i'],
                                        "page_id": p},
                                request=self.context['request'])
            canvases.append(canvas_id)

        return canvases

    def get_id(self, obj):
        return reverse('source-range-detail',
                       kwargs={"source_id": obj['source_i'],
                               "item_id": obj['pk']},
                       request=self.context['request'])

    def get_service(self, obj):
        return ServiceSerializer(obj, context={"request": self.context['request']}).data
