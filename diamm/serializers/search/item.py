import serpy
import uuid
from diamm.models.data.item_note import ItemNote


class ItemNotesSearchSerializer(serpy.Serializer):
    pk = serpy.IntField()
    id = serpy.MethodField()
    type = serpy.MethodField()

    note_type_i = serpy.IntField(
        attr="type"
    )
    note_type_s = serpy.StrField(
        attr="note_type"
    )
    note_sni = serpy.StrField(
        attr="note"
    )

    def get_id(self, obj):
        return str(uuid.uuid4())

    def get_type(self, obj):
        return obj.__class__.__name__.lower()


class ItemSearchSerializer(serpy.Serializer):
    """
        In testing, Serpy is twice as fast as DRF so we use it here
        since this is index-time performance-sensitive.
    """
    type = serpy.MethodField()
    pk = serpy.IntField()

    source_i = serpy.IntField(
        attr="source.pk"
    )
    source_s = serpy.StrField(
        attr="source.display_name"
    )
    pages_ii = serpy.MethodField()
    pages_ssni = serpy.MethodField()

    num_voices_s = serpy.StrField(
        attr="num_voices",
        required=False
    )
    composition_s = serpy.MethodField()
    composition_i = serpy.MethodField()
    item_title_s = serpy.StrField(
        attr="item_title",
        required=False
    )
    source_attribution_s = serpy.StrField(
        attr="source_attribution",
        required=False
    )
    source_incipit_s = serpy.StrField(
        attr="source_incipit",
        required=False
    )
    source_order_i = serpy.IntField(
        attr="source_order",
        required=False
    )

    folio_start_s = serpy.StrField(
        attr="folio_start",
        required=False
    )
    folio_end_s = serpy.StrField(
        attr="folio_end",
        required=False
    )
    folio_start_ans = serpy.StrField(
        attr="folio_start",
        required=False
    )
    folio_end_ans = serpy.StrField(
        attr="folio_end",
        required=False
    )
    composers_ssni = serpy.MethodField()
    composers_ss = serpy.MethodField()
    composer_ans = serpy.MethodField()
    bibliography_ii = serpy.MethodField()
    voices_ii = serpy.MethodField()
    genres_ss = serpy.MethodField()

    _childDocuments_ = serpy.MethodField()

    def get_type(self, obj):
        return obj.__class__.__name__.lower()

    def get_pages_ii(self, obj):
        return list(obj.pages.values_list('pk', flat=True))

    def get_pages_ssni(self, obj):
        pages = obj.pages.values_list('pk', 'numeration')
        page_strs = ["{0}|{1}".format(o[0], o[1]) for o in pages]
        return page_strs

    def get_composition_i(self, obj):
        if obj.composition:
            return obj.composition.pk
        return None

    def get_composition_s(self, obj):
        if obj.composition:
            return obj.composition.title
        return None

    def get_bibliography_ii(self, obj):
        if obj.itembibliography_set.count() > 0:
            return list(obj.itembibliography_set.values_list('bibliography__pk', flat=True))
        return []

    def get_composers_ssni(self, obj):
        """
            Returns a array of composer names, PK, and certainty, formatted to be split
            by the pipe (|). This is so we can store these bits of information in Solr without
            using nested documents.

            Will be broken apart on display, and the PK will be resolved to a full URL.
        """
        if obj.composition:
            if not obj.composition.anonymous:
                return ["{0}|{1}|{2}".format(c.composer.full_name, c.composer.pk, c.uncertain) for c in obj.composition.composers.all()]
            else:
                return ["Anonymous||"]
        elif obj.unattributed_composers.count() > 0:
            return ["{0}|{1}|{2}".format(c.composer.full_name, c.composer.pk, c.uncertain) for c in obj.unattributed_composers.all()]
        else:
            return []

    def get_composers_ss(self, obj):
        """
            Returns an array of composer names for the purposes of filtering and searching by name.
        """
        if obj.composition:
            if not obj.composition.anonymous:
                return ["{0}".format(c.composer.full_name) for c in obj.composition.composers.all()]
            else:
                return ["Anonymous"]
        elif obj.unattributed_composers.count() > 0:
            return ["{0}".format(c.composer.full_name) for c in obj.unattributed_composers.all()]
        else:
            return []

    def get_voices_ii(self, obj):
        if obj.voices.count() > 0:
            return list(obj.voices.values_list('pk', flat=True))
        return []

    def get_composer_ans(self, obj):
        """
            Gets the first composer and stores it in an alphanumeric sort field so that the results may be sorted
            by composer. Esp. useful in non-attributed records.
        """
        if obj.composition:
            if not obj.composition.anonymous and obj.composition.composers.count() > 0:
                return "{0}".format(obj.composition.composers.first().composer.full_name)
            else:
                return "Anonymous"
        elif obj.unattributed_composers.count() > 0:
            return "{0}".format(obj.unattributed_composers.first().composer.full_name)
        else:
            return None

    def get_genres_ss(self, obj):
        if obj.composition:
            return list(obj.composition.genres.values_list('name', flat=True))
        return []

    def get__childDocuments_(self, obj):
        return ItemNotesSearchSerializer(obj.notes.exclude(type=ItemNote.CONCORDANCES), many=True).data
