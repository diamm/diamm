import uuid
from typing import Optional

import serpy

from diamm.models.data.item_note import ItemNote


class ItemNotesSearchSerializer(serpy.Serializer):
    pk = serpy.IntField()
    id = serpy.MethodField()
    type = serpy.MethodField()

    note_type_i = serpy.IntField(attr="type")
    note_type_s = serpy.StrField(attr="note_type")
    note_sni = serpy.StrField(attr="note")

    def get_id(self, obj):
        return str(uuid.uuid4())

    def get_type(self, obj):
        return obj.__class__.__name__.lower()


class ItemSearchSerializer(serpy.Serializer):
    type = serpy.MethodField()
    pk = serpy.IntField()

    source_i = serpy.IntField(attr="source.pk")
    source_s = serpy.StrField(attr="source.display_name")
    pages_ii = serpy.MethodField()
    pages_ssni = serpy.MethodField()

    num_voices_s = serpy.StrField(attr="num_voices", required=False)
    composition_s = serpy.MethodField()
    composition_i = serpy.MethodField()
    item_title_s = serpy.StrField(attr="item_title", required=False)
    source_attribution_s = serpy.StrField(attr="source_attribution", required=False)
    source_incipit_s = serpy.StrField(attr="source_incipit", required=False)
    source_order_f = serpy.FloatField(attr="source_order", required=False)

    folio_start_s = serpy.StrField(attr="folio_start", required=False)
    folio_end_s = serpy.StrField(attr="folio_end", required=False)
    folio_start_ans = serpy.StrField(attr="folio_start", required=False)
    folio_end_ans = serpy.StrField(attr="folio_end", required=False)
    composers_ssni = serpy.MethodField()
    composers_ss = serpy.MethodField()
    composer_ans = serpy.MethodField()
    bibliography_ii = serpy.MethodField()
    voices_ii = serpy.MethodField()
    genres_ss = serpy.MethodField()

    _childDocuments_ = serpy.MethodField()

    def get_type(self, obj) -> str:
        return obj.__class__.__name__.lower()

    def get_pages_ii(self, obj) -> list[int]:
        return list(obj.pages.values_list("pk", flat=True))

    def get_pages_ssni(self, obj) -> list:
        pages = obj.pages.values_list("pk", "numeration")
        page_strs = [f"{o[0]}|{o[1]}" for o in pages]
        return page_strs

    def get_composition_i(self, obj) -> Optional[int]:
        if obj.composition:
            return obj.composition.pk
        return None

    def get_composition_s(self, obj) -> Optional[str]:
        if obj.composition:
            return obj.composition.title
        return None

    def get_bibliography_ii(self, obj) -> list[int]:
        if obj.itembibliography_set.exists():
            return list(
                obj.itembibliography_set.select_related(
                    "bibliography__type"
                ).values_list("bibliography__pk", flat=True)
            )
        return []

    def __composers(self, obj) -> list[tuple[str, Optional[int], Optional[bool]]]:
        """
        Returns an array of composer names, PK, and certainty.
        """
        composers = []
        unattr_composers = []

        if obj.composition:
            if obj.composition.anonymous:
                composers = [("Anonymous", None, None)]
            else:
                composers = [
                    (c.composer.full_name, c.composer.pk, c.uncertain)
                    for c in obj.composition.composers.all()
                ]

        if obj.unattributed_composers.exists():
            unattr_composers = [
                (c.composer.full_name, c.composer.pk, c.uncertain)
                for c in obj.unattributed_composers.all()
            ]

        return composers + unattr_composers

    def get_composers_ssni(self, obj) -> list[str]:
        """
        Returns a array of composer names, PK, and certainty, formatted to be split
        by the pipe (|). This is so we can store these bits of information in Solr without
        using nested documents.

        Will be broken apart on display, and the PK will be resolved to a full URL.
        """
        composers = self.__composers(obj)
        all_composers = []
        for composer in composers:
            c = (str(cv if cv is not None else "") for cv in composer)
            all_composers.append("|".join(c))
        return all_composers

    def get_composers_ss(self, obj):
        """
        Returns an array of composer names for the purposes of filtering and searching by name.
        """
        composers = self.__composers(obj)
        return [c[0] for c in composers]

    def get_voices_ii(self, obj):
        if obj.voices.exists():
            return list(obj.voices.values_list("pk", flat=True))
        return []

    def get_composer_ans(self, obj):
        """
        Gets the first composer and stores it in an alphanumeric sort field so that the results may be sorted
        by composer. Esp. useful in non-attributed records.
        """
        composers = self.__composers(obj)
        if len(composers) > 0:
            return composers[0][0]
        return None

    def get_genres_ss(self, obj):
        if obj.composition:
            return list(obj.composition.genres.values_list("name", flat=True))
        return []

    def get__childDocuments_(self, obj):
        return ItemNotesSearchSerializer(
            obj.notes.exclude(type=ItemNote.CONCORDANCES), many=True
        ).data
