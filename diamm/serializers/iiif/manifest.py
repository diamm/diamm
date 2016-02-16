import serpy
from diamm.serializers.iiif.ldserializer import LDSerializer
from diamm.serializers.iiif.ldfields import LDKeywordField


class Canvas(LDSerializer):
    id = LDKeywordField(
        label="@id"
    )
    type = LDKeywordField(
        label="@type"
    )
    label = serpy.StrField()
    width = serpy.IntField()
    height = serpy.IntField()


class MetadataEntry(LDSerializer):
    label = serpy.StrField()
    value = serpy.StrField()


class Sequence(LDSerializer):
    id = LDKeywordField(
        label="@id"
    )
    type = LDKeywordField(
        label="@type"
    )
    canvases = Canvas(many=True)


class Manifest(LDSerializer):
    id = LDKeywordField(
        label="@id"
    )
    context = LDKeywordField(
        label="@context"
    )
    type = LDKeywordField(
        label="@type"
    )
    description = serpy.StrField()
    attribution = serpy.StrField()
    viewingHint = serpy.StrField()
    metadata = MetadataEntry(many=True)
    sequences = Sequence(many=True)


def test():
    class MetaObj:
        def __init__(self, label, value):
            self.label = label
            self.value = value

    class CanvObj:
        id = "http://foo/bar/baz/canv"
        type = "sc:Canvas"

        def __init__(self, label, width, height):
            self.label = label
            self.width = width
            self.height = height

    class SeqObj:
        id = "http://foo/bar/baz/seq"
        type = "sc:Sequence"
        label = "Default"
        canvases = [
            CanvObj("Label 1", 1000, 1000),
            CanvObj("Label 2", 2000, 2000),
            CanvObj("Label 3", 3000, 3000)
        ]

    class ManifObj:
        id = "http://foo/bar/baz/"
        context = "http://iiif.io/api/presentation/2/context.json"
        type = "sc:Manifest"
        attribution = "DIAMM"
        viewingHint = "paged"
        metadata = [
            MetaObj('label1', 'value1'),
            MetaObj('label2', 'value2'),
            MetaObj('label3', 'value3')
        ]
        description = "Blah blah blah."
        sequences = [
            SeqObj()
        ]

    obj = ManifObj()

    ser = Manifest(obj)
    print(ser.data)
