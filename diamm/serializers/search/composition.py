import re
from functools import cache
from typing import Optional

import serpy


class CompositionSearchSerializer(serpy.Serializer):
    type = serpy.MethodField()
    pk = serpy.IntField()

    title_s = serpy.StrField(
        attr="title"
    )
    display_name_ans = serpy.StrField(
        attr="title"
    )
    anonymous_b = serpy.BoolField(
        attr="anonymous"
    )
    genres_ss = serpy.MethodField()
    composers_ssni = serpy.MethodField()
    composers_ss = serpy.MethodField()
    composers_ii = serpy.MethodField()
    voice_text_txt = serpy.MethodField()
    sources_ss = serpy.MethodField()
    sources_ssni = serpy.MethodField()
    sources_ii = serpy.MethodField()

    def get_type(self, obj):
        return obj.__class__.__name__.lower()

    def get_genres_ss(self, obj):
        if obj.genres:
            return list(obj.genres.all().values_list('name', flat=True))
        return []

    @cache
    def __composers(self, obj) -> Optional[list]:
        if obj.composers.exists():
            return [(o.composer.pk, o.composer.full_name, o.uncertain) for o in obj.composers.all()]
        return None

    def get_composers_ss(self, obj):
        composers = self.__composers(obj)

        if composers:
            return [o[1] for o in composers]
        return []

    def get_composers_ssni(self, obj):
        composers = self.__composers(obj)
        if composers:
            return [f"{o[0]}|{o[1]}|{o[2]}" for o in composers]
        return []

    def get_composers_ii(self, obj):
        composers = self.__composers(obj)
        if composers:
            return [o[0] for o in composers]
        return []

    @cache
    def __sources(self, obj) -> Optional[list]:
        if obj.sources.exists():
            return [(s.source.pk, s.source.display_name) for s in obj.sources.all()]
        return None

    def get_sources_ssni(self, obj):
        sources = self.__sources(obj)
        if sources:
            return [f"{s[0]}|{s[1]}" for s in sources]
        return []

    def get_sources_ss(self, obj):
        sources = self.__sources(obj)
        if sources:
            return [s[1] for s in sources]
        return []

    def get_sources_ii(self, obj):
        sources = self.__sources(obj)
        if sources:
            return [s[0] for s in sources]
        return []

    def get_voice_text_txt(self, obj):
        # NB: Sources == Items in this case, since the item is the relationship
        # between composition and source.
        if not obj.sources.exists():
            return None

        voice_texts = set()
        items = obj.sources.filter(voices__isnull=False, voices__voice_text__isnull=False)
        for it in items:
            for voice in it.voices.all():
                if not voice.voice_text:
                    continue
                voice_text = re.sub(r'[^\w ]+', '', voice.voice_text, flags=re.UNICODE)
                voice_text = " ".join(voice_text.split())
                voice_texts.add(voice_text)

        return list(voice_texts)
