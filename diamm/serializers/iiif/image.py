import serpy
from rest_framework.reverse import reverse
from diamm.serializers.serializers import ContextDictSerializer
from diamm.serializers.fields import StaticField


class ImageSerializer(ContextDictSerializer):
    type = StaticField(
        label="@type",
        value="oa:Annotation"
    )
    motivation = StaticField(
        value="sc:painting"
    )
    on = serpy.MethodField()
    resource = serpy.MethodField()

    def get_on(self, obj):
        page_id = self.context["page_id"]
        source_id = self.context["source_id"]
        request = self.context["request"]
        return reverse(
            "source-canvas-detail",
            kwargs={"source_id": source_id, "page_id": page_id},
            request=request
        )

    def get_resource(self, obj):
        proxied_image_url = reverse('image-serve-info',
                                    kwargs={"pk": obj['pk']},
                                    request=self.context['request'])
        return {
            "@id": proxied_image_url,
            "@type": "dctypes:Image",
            "format": "image/jpeg",
            "width": obj['width_i'],
            "height": obj['height_i'],
            "service": {
                "@context": "http://iiif.io/api/image/2/context.json",
                "@id": proxied_image_url,
                "profile": "http://iiif.io/api/image/2/level1.json"
            }
        }
