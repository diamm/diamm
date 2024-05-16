import serpy


class VoiceSearchSerializer(serpy.Serializer):
    pk = serpy.IntField()
    type = serpy.MethodField()

    label_s = serpy.StrField(
        attr="label",
        required=False
    )

    position_s = serpy.StrField(
        attr="position",
        required=False
    )
    item_i = serpy.IntField(
        attr="item.id"
    )

    voice_type_s = serpy.MethodField()

    languages_ss = serpy.MethodField()
    mensuration_s = serpy.MethodField()
    mensuration_text_s = serpy.MethodField()

    clef_s = serpy.MethodField()
    # sort_order_i = serpy.IntField(
    #     attr="sort_order"
    # )

    voice_text_s = serpy.StrField(
        attr="voice_text"
    )

    def get_voice_type_s(self, obj):
        return obj.type.name

    def get_languages_ss(self, obj):
        if obj.languages:
            return list(obj.languages.values_list('name', flat=True))
        return []

    def get_mensuration_s(self, obj):
        if obj.mensuration:
            return obj.mensuration.sign
        return None

    def get_mensuration_text_s(self, obj):
        if obj.mensuration:
            return obj.mensuration.text
        return None

    def get_clef_s(self, obj):
        if obj.clef:
            return obj.clef.name
        return None

    def get_type(self, obj):
        return obj.__class__.__name__.lower()
