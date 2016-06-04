import serpy
from rest_framework.reverse import reverse
from diamm.serializers.serializers import ContextDictSerializer
from diamm.serializers.fields import StaticField
from diamm.serializers.iiif.service import StructureServiceSerializer


class StructureSerializer(ContextDictSerializer):
    members = serpy.MethodField()
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

    def get_members(self, obj):
        if not obj.get('pages_ii'):
            return None

        members = []
        for p in obj['pages_ssni']:
            pk, name = p.split("|")
            canvas_id = reverse("source-canvas-detail",
                                kwargs={"source_id": obj['source_i'],
                                        "page_id": pk},
                                request=self.context['request'])

            member_obj = {
                "@id": canvas_id,
                "@type": "sc:Canvas",
                "label": name
            }

            members.append(member_obj)

        return members

    def get_id(self, obj):
        return reverse('source-range-detail',
                       kwargs={"source_id": obj['source_i'],
                               "item_id": obj['pk']},
                       request=self.context['request'])

    def get_service(self, obj):
        return StructureServiceSerializer(obj, context={"request": self.context['request']}).data