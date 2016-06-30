import serpy
from rest_framework.reverse import reverse
from diamm.serializers.serializers import ContextSerializer


class SourceArchiveSerializer(ContextSerializer):
    url = serpy.MethodField()
    display_name = serpy.StrField()
    has_images = serpy.MethodField()

    public_images = serpy.BoolField(
        attr="public_images"
    )

    def get_url(self, obj):
        return reverse('source-detail',
                       kwargs={"pk": obj.pk},
                       request=self.context['request'])

    def get_has_images(self, obj):
        if obj.pages.count() > 0:
            return True
        return False


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
        return SourceArchiveSerializer(obj.sources.all(),
                                       many=True,
                                       context={'request': self.context['request']}).data

    def get_logo(self, obj):
        if obj.logo:
            return obj.logo.url

class ArchiveListSerializer(ContextSerializer):
    url = serpy.MethodField()
    city = serpy.MethodField()
    name = serpy.StrField()

    def get_url(self, obj):
        return reverse('archive-detail',
                       kwargs={"pk": obj.pk},
                       request=self.context['request'])

    def get_city(self, obj):
        return CityArchiveSerializer(obj.city, context={'request': self.context['request']}).data

