import serpy
import pysolr
from django.conf import settings
# Hopefully this can be factored out when clarkduvall/serpy#16 is fixed.
from diamm.serializers.serializers import ContextSerializer, ContextDictSerializer
from rest_framework.reverse import reverse


class SourceSetSerializer(ContextDictSerializer):
    cluster_shelfmark = serpy.StrField(
        attr="cluster_shelfmark_s"
    )
    sources = serpy.MethodField()
    set_type = serpy.StrField(
        attr="set_type_s"
    )

    def get_sources(self, obj):
        source_ids = ",".join([str(id) for id in obj['sources_ii']])
        connection = pysolr.Solr(settings.SOLR['SERVER'])
        fq = ["type:source", "{!terms f=pk}"+source_ids]

        if 'source_id' in self.context:
            fq.append("-pk:{0}".format(self.context['source_id']))

        fl = ["pk", "shelfmark_s", "display_name_s"]
        sort = ["shelfmark_ans asc"]

        results = connection.search("*:*", fq=fq, fl=fl, sort=sort, rows=10000)

        if results.hits > 0:
            for doc in results.docs:
                source_url = reverse('source-detail',
                                     kwargs={"pk": doc['pk']},
                                     request=self.context['request'])
                doc['url'] = source_url

            return results.docs
        else:
            return []


class SourceBibliographySerializer(ContextDictSerializer):
    pk = serpy.IntField()
    prerendered = serpy.StrField(
        attr="prerendered_sni"
    )
    primary_study = serpy.BoolField()
    pages = serpy.StrField(
        required=False
    )
    notes = serpy.StrField(
        required=False
    )


class SourceInventorySerializer(ContextDictSerializer):
    pk = serpy.IntField()
    url = serpy.MethodField()
    folio_start = serpy.MethodField()
    folio_end = serpy.MethodField()
    composition = serpy.MethodField()
    composers = serpy.MethodField()

    def get_folio_end(self, obj):
        if 'folio_end_s' in obj:
            return obj['folio_end_s']
        else:
            return None

    def get_folio_start(self, obj):
        if 'folio_start_s' in obj:
            return obj['folio_start_s']
        else:
            return None

    def get_url(self, obj):
        if 'composition_i' in obj:
            return reverse('composition-detail',
                           kwargs={'pk': obj['composition_i']},
                           request=self.context['request'])

    def get_composition(self, obj):
        if 'composition_s' in obj:
            return obj['composition_s']
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


class SourceArchiveSerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()
    siglum = serpy.StrField()
    city = serpy.MethodField()

    def get_url(self, obj):
        return reverse('archive-detail',
                       kwargs={"pk": obj.pk},
                       request=self.context['request'])

    def get_city(self, obj):
        city_url = reverse('city-detail',
                           kwargs={"pk": obj.city_id},
                           request=self.context['request'])
        return {
            'url': city_url,
            'name': obj.city.name
        }


class SourceNoteSerializer(ContextSerializer):
    note = serpy.StrField()
    type = serpy.IntField()
    note_type = serpy.StrField()


class SourceNotationsSerializer(ContextSerializer):
    name = serpy.StrField()


class SourceIdentifierSerializer(ContextSerializer):
    identifier = serpy.StrField()
    type = serpy.IntField()
    identifier_type = serpy.StrField()
    note = serpy.StrField(
        required=False
    )


class SourceListSerializer(ContextSerializer):
    pk = serpy.IntField()
    url = serpy.MethodField()
    display_name = serpy.StrField()
    shelfmark = serpy.StrField()

    def get_url(self, obj):
        return reverse('source-detail',
                       kwargs={"pk": obj.pk},
                       request=self.context['request'])


class SourceDetailSerializer(ContextSerializer):
    pk = serpy.IntField()
    url = serpy.MethodField()
    name = serpy.StrField(
        required=False
    )
    display_name = serpy.StrField()
    shelfmark = serpy.StrField()
    surface_type = serpy.StrField()
    date_statement = serpy.StrField()
    type = serpy.StrField()
    cover_image_url = serpy.MethodField()
    manifest_url = serpy.MethodField()
    inventory_provided = serpy.BoolField()
    public_images = serpy.BoolField()

    inventory = serpy.MethodField()
    archive = serpy.MethodField()
    sets = serpy.MethodField()

    bibliography = SourceBibliographySerializer(
        attr="solr_bibliography",
        many=True
    )
    identifiers = SourceIdentifierSerializer(
        attr="identifiers.all",
        call=True,
        many=True
    )
    notations = SourceNotationsSerializer(
        attr="notations.all",
        call=True,
        many=True
    )
    notes = SourceNoteSerializer(
        attr="public_notes",
        many=True
    )

    def get_url(self, obj):
        return reverse('source-detail',
                       kwargs={"pk": obj.pk},
                       request=self.context['request'])

    def get_cover_image_url(self, obj):
        if getattr(obj, 'cover_image_id'):
            return reverse('image-serve-info',
                           kwargs={"pk": obj.cover_image_id},
                           request=self.context['request'])
        else:
            return None

    def get_manifest_url(self, obj):
        return reverse('source-manifest',
                       kwargs={"pk": obj.pk},
                       request=self.context['request'])

    def get_inventory(self, obj):
        items = obj.solr_inventory
        inventory = [SourceInventorySerializer(i, context={"request": self.context['request']}).data
                        for i in items]
        return inventory

    def get_archive(self, obj):
        return SourceArchiveSerializer(
            obj.archive,
            context={"request": self.context['request']}
        ).data

    def get_sets(self, obj):
        set_res = obj.solr_sets
        sets = [SourceSetSerializer(s, context={"request": self.context['request'],
                                                "source_id": obj.pk}).data for s in set_res]
        return sets
