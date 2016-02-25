from rest_framework.reverse import reverse
from rest_framework import serializers
from diamm.models.data.source import Source
from diamm.models.data.source_note import SourceNote
from diamm.models.data.source_identifier import SourceIdentifier
from diamm.models.data.archive import Archive
from diamm.models.data.composition import Composition
from diamm.models.data.person import Person
from diamm.models.data.composition_composer import CompositionComposer
from diamm.models.data.geographic_area import GeographicArea


class CompositionComposerSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedRelatedField(view_name="person-detail",
                                              source="composer.id",
                                              read_only=True)
    full_name = serializers.ReadOnlyField(source="composer.full_name")

    class Meta:
        model = CompositionComposer
        fields = ('url', 'full_name', 'uncertain', 'notes')


class SourceItemCompositionSerializer(serializers.HyperlinkedModelSerializer):
    composers = CompositionComposerSerializer(many=True)

    class Meta:
        model = Composition
        fields = ('url', 'name', 'composers', 'anonymous')


# class SourceItemNoteSerializer(serializers.ModelSerializer):
#     note_type = serializers.ReadOnlyField()
#
#     class Meta:
#         model = ItemNote
#         fields = ('note_type', 'type', 'note')


class AggregateComposerSerializer(serializers.HyperlinkedModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Person
        fields = ('url', 'full_name')


class SourceBibliographySerializer(serializers.Serializer):
    class Meta:
        fields = ('pk',
                  'prerendered',
                  'primary_study')

    pk = serializers.ReadOnlyField()
    prerendered = serializers.ReadOnlyField(
        source='prerendered_sni'
    )
    primary_study = serializers.ReadOnlyField()

class SourcePageSerializer(serializers.Serializer):
    class Meta:
        fields = ('pk',
                  'type',
                  'numeration',
                  'image_urls')

    numeration = serializers.ReadOnlyField(
        source='numeration_s'
    )
    image_urls = serializers.SerializerMethodField()

    def get_image_urls(self, obj):
        if 'image_urls_ss' in obj:
            return obj['image_urls_ss']
        else:
            return []


class SourceItemSerializer(serializers.Serializer):
    """
        This serializer deals with Solr results instead of results
        from the database.
    """
    class Meta:
        fields = ('pk',
                  'url',
                  'composition',
                  # 'item_type',
                  'folio_start',
                  'folio_end',
                  'composers')

    # NB: URL to the composition, not the Item.
    url = serializers.SerializerMethodField()
    composition = serializers.ReadOnlyField(
        source="composition_s"
    )
    composers = serializers.SerializerMethodField(
        source="composers_ssni"
    )
    folio_start = serializers.ReadOnlyField(
        source="folio_start_s"
    )
    folio_end = serializers.ReadOnlyField(
        source="folio_end_s"
    )

    def get_url(self, obj):
        if 'composition_i' in obj:
            return reverse('composition-detail', kwargs={'pk': obj['composition_i']}, request=self.context['request'])
        else:
            return None

    def get_composers(self, obj):
        composers = obj.get('composers_ssni')
        if not composers:
            return []

        out = []
        try:
            req = self.context['request']
        except KeyError:
            raise

        for composer in composers:
            # Unpack the composer values. See the Item Search Serializer for more info.
            full_name, pk, uncertain = composer.split("|")
            url = None

            if pk:
                url = reverse('person-detail', kwargs={"pk": int(pk)}, request=req)

            # cast the value of uncertain to a boolean. Will handle both false and empty values
            uncertain = True if uncertain == "True" else False

            out.append({
                'url': url,
                'full_name': full_name,
                'uncertain': uncertain
            })

        return out


class SourceNoteSerializer(serializers.ModelSerializer):
    note_type = serializers.ReadOnlyField()

    class Meta:
        model = SourceNote
        fields = ('note_type', 'note', 'type', 'pk')


class SourceIdentifierSerializer(serializers.ModelSerializer):
    identifier_type = serializers.ReadOnlyField()

    class Meta:
        model = SourceIdentifier
        fields = ('identifier', 'type', 'identifier_type', 'note')


class CityArchiveSourceSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name="city-detail",
    )
    class Meta:
        model = GeographicArea
        fields = ('url', 'name',)


class ArchiveSourceSerializer(serializers.HyperlinkedModelSerializer):
    city = CityArchiveSourceSerializer()

    class Meta:
        model = Archive
        fields = ('url', 'name', 'city', 'siglum')


class SourceListSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Source
        fields = ('url', 'name', 'display_name', 'shelfmark')

    display_name = serializers.ReadOnlyField()


class SourceDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Source
        fields = ('pk',
                  'url',
                  'name',
                  'archive',
                  'display_name',
                  'shelfmark',
                  'notes',
                  'identifiers',
                  'surface',
                  'surface_type',
                  'date_statement',
                  'type',
                  'inventory',
                  'bibliography',
                  'cover_image_url',
                  'pages',
                  'manifest_url')

    notes = SourceNoteSerializer(
        source="public_notes",
        many=True,
        required=False
    )
    identifiers = SourceIdentifierSerializer(
        many=True,
        required=False
    )
    archive = ArchiveSourceSerializer(
        required=False
    )
    inventory = SourceItemSerializer(
        source="solr_inventory",
        many=True,
        required=False
    )
    bibliography = SourceBibliographySerializer(
        source="solr_bibliography",
        many=True,
        required=False
    )
    pages = SourcePageSerializer(
        source="solr_pages",
        many=True,
        required=False
    )
    manifest_url = serializers.HyperlinkedIdentityField(
        view_name="source-manifest",
        source="pk",
        read_only=True
    )
    cover_image_url = serializers.HyperlinkedRelatedField(
        view_name="image-serve-info",
        source="cover_image.pk",
        read_only=True
    )
