import logging

import ypres

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
    return [CompositionSearchSerializer(record).serialized]


def _get_compositions(cfg: dict):
    sql_query = r"""WITH comp AS (
        SELECT c.*
        FROM diamm_data_composition c
    ),

                         agg_genres AS (
        SELECT
            ddcg.composition_id,
            ARRAY_AGG(ddg.name) AS genres
        FROM diamm_data_composition_genres ddcg
            LEFT JOIN diamm_data_genre ddg ON ddg.id = ddcg.genre_id
        GROUP BY ddcg.composition_id
                         ),

                         agg_comp_composers AS (
        SELECT
            cc2.composition_id,
            JSONB_AGG(DISTINCT JSONB_STRIP_NULLS(JSONB_BUILD_OBJECT(
      'id', p2.id,
      'last_name', p2.last_name,
      'first_name', p2.first_name,
      'earliest_year', p2.earliest_year,
      'latest_year', p2.latest_year,
      'earliest_year_approximate', p2.earliest_year_approximate,
      'latest_year_approximate', p2.latest_year_approximate,
      'floruit', p2.floruit,
      'uncertain', cc2.uncertain
    ))) AS composition_composers
        FROM diamm_data_compositioncomposer cc2
            LEFT JOIN diamm_data_person p2 ON p2.id = cc2.composer_id
        GROUP BY cc2.composition_id
                         ),

                         agg_sources AS (
        SELECT
            i.composition_id,
            JSONB_AGG(DISTINCT JSONB_BUILD_OBJECT(
      'id', s.id,
      'display_name',
        CONCAT_WS(
          ' ',
          a.siglum,
          s.shelfmark,
          NULLIF('(' || s.name || ')', '()')
        )
    )) AS sources
        FROM diamm_data_item i
            LEFT JOIN diamm_data_source  s ON s.id = i.source_id
            LEFT JOIN diamm_data_archive a ON a.id = s.archive_id
        GROUP BY i.composition_id
                         ),

                         agg_voice_texts AS (
        SELECT
            i.composition_id,
            ARRAY_AGG(
                    REGEXP_REPLACE(TRIM(v.voice_text), '\W+| {2,}', ' ', 'g')
            ) FILTER (
      WHERE v.voice_text IS NOT NULL AND LENGTH(v.voice_text) > 3
    ) AS voice_texts
        FROM diamm_data_item i
            LEFT JOIN diamm_data_voice v ON v.item_id = i.id
        GROUP BY i.composition_id
                         )

                    SELECT
                        c.id AS pk,
                        'composition' AS record_type,
                        c.title,
                        c.anonymous,
                        g.genres,
                        cc.composition_composers,
                        s.sources,
                        vt.voice_texts
                    FROM comp c
                        LEFT JOIN agg_genres         g  ON g.composition_id  = c.id
                        LEFT JOIN agg_comp_composers cc ON cc.composition_id = c.id
                        LEFT JOIN agg_sources        s  ON s.composition_id  = c.id
                        LEFT JOIN agg_voice_texts    vt ON vt.composition_id = c.id
                    ORDER BY c.id;"""

    return get_db_records(sql_query, cfg)


class CompositionSearchSerializer(ypres.DictSerializer):
    type = ypres.StrField(attr="record_type")
    pk = ypres.IntField(attr="pk")
    public_b = ypres.StaticField(True)
    title_s = ypres.StrField(attr="title")
    display_name_ans = ypres.StrField(attr="title")
    anonymous_b = ypres.BoolField(attr="anonymous")
    genres_ss = ypres.Field(attr="genres")
    voice_text_txt = ypres.Field(attr="voice_texts")
    composers_ssni = ypres.MethodField()
    composers_ss = ypres.MethodField()
    composers_ii = ypres.MethodField()
    sources_ss = ypres.MethodField()
    sources_ssni = ypres.MethodField()
    sources_ii = ypres.MethodField()
    composers_json = ypres.Field(attr="composition_composers")

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
