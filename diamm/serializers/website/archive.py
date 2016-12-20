import serpy
from rest_framework.reverse import reverse
from diamm.serializers.serializers import ContextSerializer, ContextDictSerializer


class SourceArchiveSerializer(ContextDictSerializer):
    url = serpy.MethodField()
    display_name = serpy.StrField(
        attr="display_name_s"
    )
    # has_images = serpy.MethodField()

    public_images = serpy.BoolField(
        attr="public_images_b"
    )
    cover_image = serpy.MethodField()

    def get_url(self, obj):
        return reverse('source-detail',
                       kwargs={"pk": obj['pk']},
                       request=self.context['request'])

    def get_cover_image(self, obj):
        if not obj.get('cover_image_i'):
            return None

        return reverse('image-serve',
                       kwargs={"pk": obj['cover_image_i'],
                               "region": "full",
                               "size": "100,",
                               "rotation": 0},
                       request=self.context['request'])


class CityArchiveSerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()
    country = serpy.StrField(
        attr="parent.name"
    )

    def get_url(self, obj):
        return reverse('city-detail',
                       kwargs={"pk": obj.pk},
                       request=self.context['request'])


class ArchiveDetailSerializer(ContextSerializer):
    url = serpy.MethodField()
    sources = serpy.MethodField()
    city = serpy.MethodField()
    former_name = serpy.StrField(
        required=False
    )
    name = serpy.StrField()
    siglum = serpy.StrField()
    website = serpy.StrField()
    logo = serpy.MethodField()

    def get_url(self, obj):
        return reverse('archive-detail',
                       kwargs={"pk": obj.pk},
                       request=self.context['request'])

    def get_city(self, obj):
        return CityArchiveSerializer(obj.city, context={'request': self.context['request']}).data

    def get_sources(self, obj):
        return SourceArchiveSerializer(obj.solr_sources,
                                       many=True,
                                       context={'request': self.context['request']}).data

    def get_logo(self, obj):
        if obj.logo:
            return obj.logo.url
