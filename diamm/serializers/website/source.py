from typing import List, Optional, Dict

import serpy
from django.conf import settings
from rest_framework.reverse import reverse

from diamm.helpers.solr_helpers import SolrManager
from diamm.serializers.serializers import ContextSerializer, ContextDictSerializer


class SourceCatalogueEntrySerializer(ContextSerializer):
    entry = serpy.MethodField()
    order = serpy.IntField()

    def get_entry(self, obj) -> str:
        request = self.context['request']
        return "{0}://{1}/media/rism/catalogue/{2}".format(
            request.scheme,
            request.get_host(),
            obj.entry
        )


class SourceCopyistSerializer(ContextDictSerializer):
    copyist = serpy.MethodField()
    uncertain = serpy.BoolField(
        attr="uncertain_b",
        required=False
    )
    type = serpy.StrField(
        attr="type"
    )
    type_s = serpy.StrField(
        attr="type_s"
    )

    def get_copyist(self, obj) -> Dict:
        url = reverse('{0}-detail'.format(obj['copyist_type_s']),
                      kwargs={"pk": int(obj['copyist_pk_i'])},
                      request=self.context['request'])
        return {
            'name': obj['copyist_s'],
            'url': url
        }


class SourceRelationshipSerializer(ContextDictSerializer):
    related_entity = serpy.MethodField()
    uncertain = serpy.BoolField(
        attr="uncertain_b",
        required=False
    )
    relationship_type = serpy.StrField(
        attr="relationship_type_s"
    )

    def get_related_entity(self, obj):
        if 'related_entity_s' in obj:
            url = reverse("{0}-detail".format(obj['related_entity_type_s']),
                          kwargs={"pk": int(obj['related_entity_pk_i'])},
                          request=self.context['request'])
            return {
                'name': obj['related_entity_s'],
                'url': url
            }
        else:
            return None


class SourceProvenanceSerializer(ContextDictSerializer):
    city = serpy.MethodField()
    country = serpy.MethodField()
    region = serpy.MethodField()
    protectorate = serpy.MethodField()
    entity = serpy.MethodField()
    country_uncertain = serpy.BoolField(
        attr="country_uncertain_b"
    )
    city_uncertain = serpy.BoolField(
        attr="city_uncertain_b"
    )
    entity_uncertain = serpy.BoolField(
        attr="entity_uncertain_b"
    )
    region_uncertain = serpy.BoolField(
        attr="region_uncertain_b"
    )

    def get_city(self, obj):
        if 'city_s' in obj:
            return obj['city_s']
        return None

    def get_country(self, obj):
        if 'country_s' in obj:
            return obj['country_s']
        return None

    def get_region(self, obj):
        if 'region_s' in obj:
            return obj['region_s']
        return None

    def get_protectorate(self, obj):
        if 'protectorate_s' in obj:
            return obj['protectorate_s']
        return None

    def get_entity(self, obj):
        if 'entity_s' in obj:
            url = reverse("{0}-detail".format(obj['entity_type_s']),
                          kwargs={"pk": int(obj['entity_pk_i'])},
                          request=self.context['request'])
            return {
                'name': obj['entity_s'],
                'url': url
            }
        else:
            return None


class SourceSetSerializer(ContextDictSerializer):
    cluster_shelfmark = serpy.StrField(
        attr="cluster_shelfmark_s"
    )
    sources = serpy.MethodField()
    set_type = serpy.StrField(
        attr="set_type_s"
    )

    def get_sources(self, obj) -> List:
        source_ids = ",".join([str(sid) for sid in obj['sources_ii']])
        connection = SolrManager(settings.SOLR['SERVER'])
        fq = ["type:source", "{!terms f=pk}"+source_ids]

        # Filter out the current source from the list of returned sources.
        if 'source_id' in self.context:
            fq.append("-pk:{0}".format(self.context['source_id']))

        fl = ["pk", "shelfmark_s", "display_name_s", "cover_image_i"]
        sort = "shelfmark_ans asc"

        connection.search("*:*", fq=fq, fl=fl, sort=sort, rows=100)

        resultlist = []

        if connection.hits > 0:
            for doc in connection.results:

                source_url = reverse('source-detail',
                                     kwargs={"pk": doc['pk']},
                                     request=self.context['request'])

                doc['url'] = source_url
                if doc.get('cover_image_i'):
                    doc['cover_image'] = reverse('image-serve-info',
                                                 kwargs={"pk": doc["cover_image_i"]},
                                                 request=self.context['request'])
                else:
                    doc['cover_image'] = None

                resultlist.append(doc)

            return resultlist
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


class SourceComposerInventoryCompositionSerializer(ContextDictSerializer):
    folio_start = serpy.StrField(
        attr="folio_start_s",
        required=False
    )
    folio_end = serpy.StrField(
        attr="folio_end_s",
        required=False
    )
    uncertain = serpy.BoolField(
        attr="uncertain_b",
        required=False
    )

    source_attribution = serpy.MethodField()

    composition = serpy.StrField(
        attr="composition_s",
        required=False
    )
    url = serpy.MethodField()

    def get_source_attribution(self, obj) -> Optional[str]:
        if 'source_attribution_i' in obj:
            return obj['source_attribution_i']
        return None

    def get_url(self, obj):
        if 'composition_i' not in obj:
            return None

        return reverse("composition-detail",
                       kwargs={"pk": obj['composition_i']},
                       request=self.context['request'])


class SourceComposerInventorySerializer(ContextDictSerializer):
    url = serpy.MethodField(
        required=False
    )
    name = serpy.StrField(
        attr="composer"
    )
    inventory = serpy.MethodField(
        required=False
    )

    def get_inventory(self, obj):
        return SourceComposerInventoryCompositionSerializer(
            obj['inventory'],
            many=True,
            context={"request": self.context['request']}
        ).data

    def get_url(self, obj):
        if 'pk' in obj and obj.get('pk'):
            return reverse('person-detail',
                           kwargs={"pk": obj['pk']},
                           request=self.context["request"])
        return None


class SourceInventoryNoteSerializer(serpy.DictSerializer):
    note = serpy.StrField(
        attr="note_sni"
    )
    note_type = serpy.StrField(
        attr="note_type_s"
    )


class SourceInventorySerializer(ContextDictSerializer):
    pk = serpy.IntField()
    url = serpy.MethodField()
    num_voices = serpy.MethodField(
        required=False
    )
    genres = serpy.MethodField(
        required=False
    )
    folio_start = serpy.MethodField(
        required=False
    )
    folio_end = serpy.MethodField(
        required=False
    )
    composition = serpy.MethodField(
        required=False
    )
    composers = serpy.MethodField(
        required=False
    )
    bibliography = serpy.MethodField(
        required=False
    )
    voices = serpy.MethodField(
        required=False
    )
    pages = serpy.MethodField(
        required=False
    )
    source_attribution = serpy.MethodField(
        required=False
    )
    notes = serpy.MethodField(
        required=False
    )

    def get_pages(self, obj):
        if 'pages_ii' in obj:
            return obj['pages_ii']
        return None

    def get_source_attribution(self, obj):
        if 'source_attribution_s' in obj:
            return obj['source_attribution_s']
        return None

    def get_num_voices(self, obj):
        if 'num_voices_s' in obj:
            return obj['num_voices_s']
        return None

    def get_genres(self, obj):
        if 'genres_ss' in obj:
            return obj['genres_ss']
        return None

    def get_notes(self, obj):
        if '_childDocuments_' in obj:
            return SourceInventoryNoteSerializer(obj['_childDocuments_'], many=True).data
        return None

    # @TODO Finish Item Bibliography stuff.
    def get_bibliography(self, obj):
        connection = SolrManager(settings.SOLR['SERVER'])
        fq = ["type:itembibliography", "item_i:{0}".format(obj['pk'])]
        sort = "prerendered_s asc"
        fl = ["pages_s", "prerendered_s", "notes_s"]

        connection.search("*:*", fq=fq, fl=fl, sort=sort, rows=100)
        return list(connection.results)

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

    def get_voices(self, obj) -> Optional[List]:
        if not obj.get('voices_ii', None):
            return None

        connection = SolrManager(settings.SOLR['SERVER'])
        id_list = ",".join(str(x) for x in obj.get('voices_ii'))
        fq = ["type:voice", "{!terms f=pk}"+id_list]
        fl = ["mensuration_s",
              "mensuration_text_s",
              "clef_s",
              "languages_ss",
              "voice_text_s",
              "voice_type_s"]

        connection.search("*:*", fq=fq, fl=fl, rows=100)
        return list(connection.results)


class SourceArchiveSerializer(ContextSerializer):
    url = serpy.MethodField()
    name = serpy.StrField()
    siglum = serpy.StrField()
    city = serpy.StrField(
        attr='city.name'
    )
    country = serpy.StrField(
        attr='city.parent.name',
        required=False
    )
    logo = serpy.MethodField()

    def get_url(self, obj):
        return reverse('archive-detail',
                       kwargs={"pk": obj.pk},
                       request=self.context['request'])

    def get_logo(self, obj):
        if obj.logo:
            return obj.logo.url


class SourceNoteSerializer(ContextSerializer):
    note = serpy.StrField()
    author = serpy.StrField()
    type = serpy.IntField()
    pk = serpy.IntField()
    note_type = serpy.StrField()


class SourceURLSerializer(ContextSerializer):
    type = serpy.IntField()
    url_type = serpy.StrField(
        attr="url_type"
    )
    link = serpy.StrField()
    link_text = serpy.StrField()


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
    display_name = serpy.StrField(
        required=False
    )
    shelfmark = serpy.StrField()
    surface_type = serpy.StrField(
        required=False
    )
    date_statement = serpy.StrField()
    source_type = serpy.StrField(
        attr="type"
    )
    format = serpy.StrField(
        required=False
    )
    measurements = serpy.StrField(
        required=False
    )
    type = serpy.MethodField()
    cover_image_info = serpy.MethodField(
        required=False
    )
    manifest_url = serpy.MethodField(
        required=False
    )
    inventory_provided = serpy.BoolField()
    public_images = serpy.BoolField()
    numbering_system_type = serpy.StrField(
        attr="numbering_system_type"
    )

    has_images = serpy.MethodField(
        required=False
    )
    inventory = serpy.MethodField(
        required=False
    )
    composer_inventory = serpy.MethodField(
        required=False
    )
    uninventoried = serpy.MethodField(
        required=False
    )
    archive = serpy.MethodField(
        required=False
    )
    sets = serpy.MethodField(
        required=False
    )
    provenance = serpy.MethodField(
        required=False
    )
    relationships = serpy.MethodField(
        required=False
    )
    copyists = serpy.MethodField(
        required=False
    )
    catalogue_entries = serpy.MethodField(
        required=False
    )
    # iiif_manifest = serpy.MethodField()

    links = SourceURLSerializer(
        attr="links.all",
        call=True,
        many=True
    )

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
    notes = serpy.MethodField(
        required=False
    )

    def get_type(self, obj):
        return obj.__class__.__name__.lower()

    def get_url(self, obj):
        return reverse('source-detail',
                       kwargs={"pk": obj.pk},
                       request=self.context['request'])

    def get_notes(self, obj):
        return SourceNoteSerializer(obj.public_notes.order_by('type', 'sort'),
                                    many=True,
                                    context={"request": self.context['request']}).data

    def get_cover_image_info(self, obj):
        try:
            cover_obj = obj.cover
        except AttributeError:
            return None

        if not cover_obj:
            return None

        obj = {
            'url': reverse('image-serve-info',
                           kwargs={"pk": cover_obj['id']},
                           request=self.context['request']),
            'label': cover_obj['label']
        }
        return obj

    def get_has_images(self, obj):
        if obj.pages.count() > 0:
            return True
        return False

    def get_manifest_url(self, obj):
        # Return None if the document has no public images
        if not self.context['request'].user.is_authenticated:
            return None

        if not self.get_has_images(obj):
            return None

        return reverse('source-manifest',
                       kwargs={"pk": obj.pk},
                       request=self.context['request'])

    def get_inventory(self, obj):
        return SourceInventorySerializer(obj.solr_inventory,
                                         many=True,
                                         context={"request": self.context['request']}).data

    def get_composer_inventory(self, obj):
        return SourceComposerInventorySerializer(obj.inventory_by_composer,
                                                 many=True,
                                                 context={"request": self.context['request']}).data

    def get_uninventoried(self, obj):
        return SourceInventorySerializer(obj.solr_uninventoried,
                                         many=True,
                                         context={"request": self.context['request']}).data

    def get_archive(self, obj):
        return SourceArchiveSerializer(obj.archive,
                                       context={"request": self.context['request']}).data

    def get_sets(self, obj):
        return SourceSetSerializer(obj.solr_sets,
                                   many=True,
                                   context={"request": self.context['request'],
                                            "source_id": obj.pk}).data

    def get_provenance(self, obj):
        return SourceProvenanceSerializer(obj.solr_provenance,
                                          many=True,
                                          context={"request": self.context['request']}).data

    def get_relationships(self, obj):
        return SourceRelationshipSerializer(obj.solr_relationships,
                                            many=True,
                                            context={"request": self.context['request']}).data

    def get_copyists(self, obj):
        return SourceCopyistSerializer(obj.solr_copyists,
                                       many=True,
                                       context={"request": self.context['request']}).data

    def get_catalogue_entries(self, obj):
        if obj.catalogue_entries.count() > 0:
            return SourceCatalogueEntrySerializer(obj.catalogue_entries.all(),
                                                  context={"request": self.context['request']},
                                                  many=True).data
        return []
