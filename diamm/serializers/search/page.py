import uuid

import serpy
import ujson


class ImageChildSerializer(serpy.Serializer):
    type = serpy.MethodField()
    pk = serpy.IntField()
    id = serpy.MethodField()

    location_s = serpy.StrField(attr="location", required=False)
    image_type_i = serpy.IntField(attr="type.pk")
    image_type_s = serpy.StrField(attr="type.name")

    width_i = serpy.MethodField()
    height_i = serpy.MethodField()
    external_b = serpy.BoolField(attr="external")

    def get_width_i(self, obj) -> int:
        if not obj.iiif_response_cache:
            return 0

        d = ujson.loads(obj.iiif_response_cache)
        if "width" in d:
            return d["width"]
        return 0

    def get_height_i(self, obj) -> int:
        if not obj.iiif_response_cache:
            return 0

        d = ujson.loads(obj.iiif_response_cache)
        if "height" in d:
            return d["height"]
        return 0

    def get_id(self, obj) -> str:
        """
        Solr doesn't provide an auto-UUID field for a childDocument,
        so we have to generate one here.
        """
        return str(uuid.uuid4())

    def get_type(self, obj):
        return obj.__class__.__name__.lower()


class PageSearchSerializer(serpy.Serializer):
    type = serpy.MethodField()
    pk = serpy.IntField()
    page_type_i = serpy.IntField(attr="page_type", required=False)
    page_type_s = serpy.StrField(attr="page_kind", required=False)

    _childDocuments_ = ImageChildSerializer(attr="public_images", many=True)
    numeration_s = serpy.StrField(attr="numeration")
    # Alphanumeric sort for the page numeration
    numeration_ans = serpy.StrField(attr="numeration")
    sort_order_f = serpy.FloatField(attr="sort_order")
    source_i = serpy.IntField(attr="source.pk")
    items_ii = serpy.MethodField()
    images_ss = serpy.MethodField()
    iiif_canvas_uri_s = serpy.StrField(attr="iiif_canvas_uri")
    external_b = serpy.BoolField(attr="external")

    def get_items_ii(self, obj):
        if obj.items.exists():
            return list(obj.items.all().values_list("pk", flat=True))
        return []

    def get_images_ss(self, obj):
        if obj.images.exists():
            return list(
                obj.images.filter(public=True).values_list("location", flat=True)
            )
        return []

    def get_type(self, obj):
        return obj.__class__.__name__.lower()
