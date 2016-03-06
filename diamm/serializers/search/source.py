import serpy


class SourceSearchSerializer(serpy.Serializer):
    type = serpy.MethodField()
    pk = serpy.IntField()

    shelfmark_s = serpy.StrField(
        attr='shelfmark'
    )
    # Alphanumeric sort field
    shelfmark_ans = serpy.StrField(
        attr='shelfmark'
    )
    name_s = serpy.StrField(
        attr="name"
    )
    display_name_s = serpy.StrField(
        attr="display_name"
    )
    archive_s = serpy.StrField(
        attr="archive.name"
    )
    surface_type_s = serpy.StrField(
        attr="surface_type"
    )
    source_type_s = serpy.StrField(
        attr="type"
    )
    date_statement_s = serpy.StrField(
        attr="date_statement"
    )
    measurements_s = serpy.StrField(
        attr="measurements"
    )
    inventory_provided_s = serpy.BoolField(
        attr="inventory_provided"
    )

    identifiers_ss = serpy.MethodField()
    notations_ss = serpy.MethodField()

    sets_ii = serpy.MethodField()
    notes_txt = serpy.MethodField()

    start_date_i = serpy.IntField(
        attr="start_date",
        required=False
    )
    end_date_i = serpy.IntField(
        attr="end_date",
        required=False
    )
    composers_ss = serpy.MethodField()
    cover_image_i = serpy.IntField(
        attr='cover_image_id',
        required=False
    )

    def get_type(self, obj):
        return obj.__class__.__name__.lower()

    def get_identifiers_ss(self, obj):
        if obj.identifiers.count() > 0:
            return list(obj.identifiers.all().values_list('identifier', flat=True))
        else:
            return []

    def get_notations_ss(self, obj):
        if obj.notations.count() > 0:
            return list(obj.notations.all().values_list('name', flat=True))
        else:
            return []

    def get_sets_ii(self, obj):
        if obj.sets.count() > 0:
            return list(obj.sets.all().values_list("pk", flat=True))
        else:
            return []

    def get_composers_ss(self, obj):
        return obj.composers

    def get_notes_txt(self, obj):
        return list(obj.public_notes.values_list('note', flat=True))
