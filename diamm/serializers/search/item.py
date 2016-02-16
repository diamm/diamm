import serpy


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

    composition_s = serpy.MethodField()
    composition_i = serpy.MethodField()

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

    def get_type(self, obj):
        return obj.__class__.__name__.lower()

    def get_composition_i(self, obj):
        if obj.composition:
            return obj.composition.pk
        return None

    def get_composition_s(self, obj):
        if obj.composition:
            return obj.composition.name
        return None

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
        elif obj.aggregate_composer:
            # Aggregate composers do not have a truth attached to their certainty.
            return ["{0}|{1}|False".format(obj.aggregate_composer.full_name,
                                           obj.aggregate_composer.pk)]
        else:
            return []
