import serpy
import re


class CompositionSearchSerializer(serpy.Serializer):
    type = serpy.MethodField()
    pk = serpy.IntField()

    title_s = serpy.StrField(
        attr="title"
    )
    genres_ss = serpy.MethodField()
    composers_ss = serpy.MethodField()
    voice_text_txt = serpy.MethodField()

    def get_type(self, obj):
        return obj.__class__.__name__.lower()

    def get_genres_ss(self, obj):
        if obj.genres:
            return list(obj.genres.all().values_list('name', flat=True))
        return []

    def get_composers_ss(self, obj):
        if obj.composers:
            return [o.composer.full_name for o in obj.composers.all()]
        return []

    def get_voice_text_txt(self, obj):
        # NB: Sources == Items in this case, since the item is the relationship
        # between composition and source.
        if obj.sources.count() == 0:
            return None

        voice_texts = []
        items = obj.sources.all()
        for it in items:
            if it.voice_set.count() == 0:
                continue

            voices = it.voice_set.all()
            for voice in voices:
                if not voice.voice_text:
                    continue

                voice_text = re.sub(r'[^\w ]+', '', voice.voice_text, flags=re.UNICODE)
                voice_text = " ".join(voice_text.split())

                if voice_text in voice_texts:
                    # It's a duplicate text, so we'll not index it
                    # to prevent improper weighting of results
                    continue

                voice_texts.append(voice_text)

        return voice_texts
