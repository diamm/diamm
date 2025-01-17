from typing import Optional

import serpy


class SourceSearchSerializer(serpy.Serializer):
    """
    For these search serializers, it is important to note that
    the field name in the serializer corresponds to the Solr field
    name, and the underscore suffix creates a dynamic field for that
    entry. So `shelfmark_s` will supply the `shelfmark_s` field in Solr,
    using the `_s` suffix to indicate that it is a non-multivalued string.

    To see what each suffix does, you should consult the Solr schema.

    The `_ans` field is a special field that provides alphanumeric sorting for
    entries. This is critical to proper display of source shelfmarks and other
    fields that might have mixed number, letter, and punctuation representations.
    "MS Add. 10" should sort between "MS Add. 9" and "MS Add. 11", which it will not
     do by default.

    """

    type = serpy.MethodField()
    pk = serpy.IntField()

    shelfmark_s = serpy.StrField(attr="shelfmark")
    name_s = serpy.StrField(attr="name", required=False)
    display_name_s = serpy.StrField(attr="display_name")
    archive_s = serpy.StrField(attr="archive.name")
    archive_i = serpy.IntField(attr="archive.pk")
    archive_city_s = serpy.StrField(attr="archive.city.name")
    archive_country_s = serpy.StrField(attr="archive.city.parent.name")
    surface_type_s = serpy.StrField(attr="surface_type", required=False)
    source_type_s = serpy.StrField(attr="type", required=False)
    date_statement_s = serpy.StrField(attr="date_statement", required=False)
    measurements_s = serpy.StrField(attr="measurements", required=False)
    inventory_provided_b = serpy.BoolField(attr="inventory_provided")

    number_of_compositions_i = serpy.IntField(attr="num_compositions")

    number_of_composers_i = serpy.IntField(attr="num_composers")

    identifiers_ss = serpy.MethodField()
    notations_ss = serpy.MethodField()

    sets_ii = serpy.MethodField()
    sets_ssni = serpy.MethodField()
    notes_txt = serpy.MethodField()

    start_date_i = serpy.IntField(attr="start_date", required=False)
    end_date_i = serpy.IntField(attr="end_date", required=False)
    composers_ss = serpy.MethodField()
    cover_image_i = serpy.MethodField()
    public_images_b = serpy.MethodField()
    open_images_b = serpy.BoolField(attr="open_images")
    external_images_b = serpy.BoolField(attr="has_external_images")

    def get_type(self, obj):
        return obj.__class__.__name__.lower()

    def get_identifiers_ss(self, obj) -> list:
        if obj.identifiers.exists():
            return list(obj.identifiers.values_list("identifier", flat=True))
        return []

    def get_cover_image_i(self, obj) -> Optional[int]:
        c = obj.cover
        return c.get("id") if c else None

    def get_notations_ss(self, obj) -> list:
        if obj.notations.exists():
            return list(obj.notations.values_list("name", flat=True))
        return []

    def get_sets_ii(self, obj) -> list:
        if obj.sets.exists():
            return list(obj.sets.values_list("pk", flat=True))
        return []

    def get_sets_ssni(self, obj) -> list:
        """
        PK|Name for the sets this source belongs to, except project sets (type=7)
        """
        if obj.sets.exists():
            sourcesets = obj.sets.values_list("pk", "cluster_shelfmark")
            sets = [f"{sset[0]}|{sset[1]}" for sset in sourcesets]
            return sets
        return []

    def get_composers_ss(self, obj) -> list:
        return obj.composers

    def get_notes_txt(self, obj) -> list:
        return list(obj.public_notes.values_list("note", flat=True))

    def get_public_images_b(self, obj) -> bool:
        has_images = obj.pages.exists()
        public_images = obj.public_images

        return has_images and public_images is not None

    def get_external_images_b(self, obj) -> bool:
        return obj.external_images
