import serpy
import uuid
import ujson


class ImageChildSerializer(serpy.Serializer):
    type = serpy.MethodField()
    pk = serpy.IntField()
    id = serpy.MethodField()

    location_s = serpy.StrField(
        attr="location"
    )
    image_type_i = serpy.IntField(
        attr="type.pk"
    )
    image_type_s = serpy.StrField(
        attr="type.name"
    )

    width_i = serpy.MethodField()
    height_i = serpy.MethodField()

    def get_width_i(self, obj):
        if obj.iiif_response_cache:
            d = ujson.loads(obj.iiif_response_cache)
            if 'width' in d:
                return d['width']
            else:
                return 0
        else:
            return 0

    def get_height_i(self, obj):
        if obj.iiif_response_cache:
            d = ujson.loads(obj.iiif_response_cache)
            if 'height' in d:
                return d['height']
            else:
                return 0
        else:
            return 0

    def get_id(self, obj):
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

    _childDocuments_ = ImageChildSerializer(
        attr="public_images",
        many=True
    )
    numeration_s = serpy.StrField(
        attr="numeration"
    )
    # Alphanumeric sort for the page numeration
    numeration_ans = serpy.StrField(
        attr="numeration"
    )
    sort_order_i = serpy.IntField(
        attr="sort_order"
    )
    source_i = serpy.IntField(
        attr="source.pk"
    )
    items_ii = serpy.MethodField()
    images_ss = serpy.MethodField()

    def get_items_ii(self, obj):
        if obj.items.count() > 0:
            return list(obj.items.all().values_list('pk', flat=True))
        else:
            return []

    def get_images_ss(self, obj):
        if obj.images.count() > 0:
            return list(obj.images.all().values_list('location', flat=True))
        else:
            return []

    def get_type(self, obj):
        return obj.__class__.__name__.lower()

