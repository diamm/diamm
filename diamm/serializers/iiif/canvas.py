import serpy
from rest_framework.reverse import reverse
from diamm.serializers.serializers import ContextDictSerializer
from diamm.serializers.fields import StaticField
from diamm.serializers.iiif.image import ImageSerializer


class CanvasSerializer(ContextDictSerializer):
    id = serpy.MethodField(
        label="@id"
    )
    type = StaticField(
        value="sc:Canvas",
        label="@type"
    )
    label = serpy.StrField(
        attr="numeration_s"
    )
    images = serpy.MethodField()
    width = serpy.MethodField()
    height = serpy.MethodField()

    def get_width(self, obj):
        if not '_childDocuments_' in obj:
            return 0
        return obj['_childDocuments_'][0]['width_i']

    def get_height(self, obj):
        if not '_childDocuments_' in obj:
            return 0

        return obj['_childDocuments_'][0]['height_i']

    def get_id(self, obj):
        return reverse(
            "source-canvas-detail",
            kwargs={"source_id": obj['source_i'],
                    "page_id": obj['pk']},
            request=self.context['request']
        )

    def get_images(self, obj):
        if not '_childDocuments_' in obj:
            return []

        imgs = obj['_childDocuments_']
        context = {
            "source_id": obj["source_i"],
            "page_id": obj["pk"],
            "request": self.context['request']
        }
        imgs_data = [ImageSerializer(i, context=context).data for i in imgs]
        return imgs_data
