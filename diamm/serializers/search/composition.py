import logging

import serpy

from diamm.serializers.fields import StaticField
from diamm.serializers.search.helpers import (
    get_db_records,
    parallelise,
    process_composers,
    process_sources,
    record_indexer,
)

log = logging.getLogger("diamm")


def index_compositions(cfg: dict) -> bool:
    log.info("Indexing compositions")
    record_groups = _get_compositions(cfg)
    parallelise(record_groups, record_indexer, create_composition_index_documents, cfg)

    return True


def create_composition_index_documents(record, cfg) -> list[dict]:
    return [CompositionSearchSerializer(record).data]


def _get_compositions(cfg: dict):
    sql_query = r"""SELECT c.id AS pk, 'composition' AS record_type, c.title AS title,
                   c.anonymous AS anonymous,
                   (SELECT array_agg(ddg.name)
                        FROM diamm_data_composition_genres AS ddcg
                        LEFT JOIN diamm_data_genre AS ddg ON ddcg.genre_id = ddg.id
                        WHERE ddcg.composition_id = c.id)
                   AS genres,
                   (SELECT jsonb_agg(DISTINCT jsonb_build_object(
                           'id', p2.id,
                           'last_name', p2.last_name,
                           'first_name', p2.first_name,
                           'earliest_year', p2.earliest_year,
                           'latest_year', p2.latest_year,
                           'earliest_year_approximate', p2.earliest_year_approximate,
                           'latest_year_approximate', p2.latest_year_approximate,
                           'floruit', p2.floruit,
                           'uncertain', cc2.uncertain
                            ))
                            FROM diamm_data_compositioncomposer AS cc2
                            LEFT JOIN diamm_data_person AS p2 ON cc2.composer_id = p2.id
                        WHERE c.id = cc2.composition_id)
                    AS composition_composers,
                   (SELECT jsonb_agg(DISTINCT jsonb_build_object(
                            'id', s.id,
                            'display_name', concat(a.siglum, ' ', s.shelfmark, coalesce(' (' || s.name || ')', ''))
                            ))
                        FROM diamm_data_item AS i
                        LEFT JOIN diamm_data_source AS s ON i.source_id = s.id
                        LEFT JOIN diamm_data_archive AS a ON s.archive_id = a.id
                        WHERE i.composition_id = c.id)
                   AS sources,
                  ( SELECT array_agg(regexp_replace(TRIM(v.voice_text), '\W+| {2,}', ' ', 'g'))
                    FROM diamm_data_item AS i
                    LEFT JOIN diamm_data_voice AS v ON v.item_id = i.id
                    WHERE i.composition_id = c.id AND LENGTH(v.voice_text) > 3 AND v.voice_text IS NOT NULL)
                  AS voice_texts
                FROM diamm_data_composition AS c
                ORDER BY c.id"""

    return get_db_records(sql_query, cfg)


class CompositionSearchSerializer(serpy.DictSerializer):
    type = serpy.StrField(attr="record_type")
    pk = serpy.IntField(attr="pk")
    public_b = StaticField(True)
    title_s = serpy.StrField(attr="title")
    display_name_ans = serpy.StrField(attr="title")
    anonymous_b = serpy.BoolField(attr="anonymous")
    genres_ss = serpy.Field(attr="genres")
    voice_text_txt = serpy.Field(attr="voice_texts")
    composers_ssni = serpy.MethodField()
    composers_ss = serpy.MethodField()
    composers_ii = serpy.MethodField()
    sources_ss = serpy.MethodField()
    sources_ssni = serpy.MethodField()
    sources_ii = serpy.MethodField()

    def get_composers_ss(self, obj):
        """
        Returns an array of composer names for the purposes of filtering and searching by name.
        """
        ret = []
        if obj.get("anonymous"):
            ret.append("Anonymous")

        composers = process_composers(
            obj.get("composition_composers"), obj.get("unattributed_composers")
        )
        return ret + [c[0] for c in composers]

    def get_composers_ssni(self, obj) -> list[str]:
        """
        Returns a array of composer names, PK, and certainty, formatted to be split
        by the pipe (|). This is so we can store these bits of information in Solr without
        using nested documents.

        Will be broken apart on display, and the PK will be resolved to a full URL.
        """
        composers = process_composers(
            obj.get("composition_composers"), obj.get("unattributed_composers")
        )
        all_composers = []
        if obj.get("anonymous_composition"):
            all_composers.append("Anonymous||")

        for composer in composers:
            name, pk, uncertain = composer
            all_composers.append(
                f"{name}|{pk if pk is not None else ''}|{uncertain if uncertain is not None else ''}",
            )
        return all_composers

    def get_composers_ii(self, obj):
        """
        Returns an array of composer names for the purposes of filtering and searching by name.
        """
        composers = process_composers(
            obj.get("composition_composers"), obj.get("unattributed_composers")
        )
        return [c[1] for c in composers]

    def get_sources_ssni(self, obj):
        sources = process_sources(obj["sources"])
        return [f"{s[0]}|{s[1]}" for s in sources]

    def get_sources_ss(self, obj):
        sources = process_sources(obj["sources"])
        return [s[1] for s in sources]

    def get_sources_ii(self, obj):
        sources = process_sources(obj["sources"])
        return [s[0] for s in sources]
