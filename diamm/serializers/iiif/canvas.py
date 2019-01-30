import operator
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
        if '_childDocuments_' not in obj:
            return 0
        # Get the dimensions from the first image in the result list, which should be the primary image.
        obj['_childDocuments_'].sort(key=operator.itemgetter('image_type_i'))
        return obj['_childDocuments_'][0]['width_i']

    def get_height(self, obj):
        if '_childDocuments_' not in obj:
            return 0
        obj['_childDocuments_'].sort(key=operator.itemgetter('image_type_i'))
        return obj['_childDocuments_'][0]['height_i']

    def get_id(self, obj):
        return reverse(
            "source-canvas-detail",
            kwargs={"source_id": obj['source_i'],
                    "page_id": obj['pk']},
            request=self.context['request']
        )

    def get_images(self, obj):
        if '_childDocuments_' not in obj:
            return []

        obj['_childDocuments_'].sort(key=operator.itemgetter('image_type_i'))
        context = {
            "source_id": obj["source_i"],
            "page_id": obj["pk"],
            "request": self.context['request']
        }

        # the 'images' key is always an array.
        imgs_data = [ImageSerializer(obj, context=context).data]
        return imgs_data
