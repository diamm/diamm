import logging

import serpy

from diamm.serializers.search.helpers import (
    get_db_records,
    parallelise,
    process_composers,
    record_indexer,
)

log = logging.getLogger("diamm")


def _get_items(cfg: dict):
    sql_query = """SELECT 'item' AS type, i.id AS pk, i.source_id AS "source.pk",
       concat(a.siglum, ' ', s.shelfmark, coalesce(' (' || s.name || ')', ''))  AS "source.display_name",
       (SELECT array_agg(ddip.page_id)
        FROM diamm_data_item_pages AS ddip
        WHERE ddip.item_id = i.id)
           AS page_ids,
       (SELECT array_agg(CONCAT(p.id, '|', p.numeration))
        FROM diamm_data_item_pages AS ddip
                 LEFT JOIN diamm_data_page AS p ON ddip.page_id = p.id
        WHERE ddip.item_id = i.id)
           AS page_numeration,
       i.num_voices AS num_voices, i.item_title AS item_title, i.source_attribution AS source_attribution,
       NULLIF(i.source_incipit, '') AS source_incipit, i.source_order AS source_order,
       i.folio_start AS folio_start, i.folio_end AS folio_end,
       i.composition_id AS composition, c.title AS composition_title,
       c.anonymous AS anonymous_composition,
       (SELECT jsonb_agg(jsonb_build_object(
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
                 LEFT JOIN diamm_data_composition AS c2 ON cc2.composition_id = c2.id
                 LEFT JOIN diamm_data_person AS p2 ON cc2.composer_id = p2.id
        WHERE i.composition_id = cc2.composition_id)
           AS composition_composers,
       (SELECT jsonb_agg(jsonb_build_object(
               'id', p2.id,
               'last_name', p2.last_name,
               'first_name', p2.first_name,
               'earliest_year', p2.earliest_year,
               'latest_year', p2.latest_year,
               'earliest_year_approximate', p2.earliest_year_approximate,
               'latest_year_approximate', p2.latest_year_approximate,
               'floruit', p2.floruit,
               'uncertain', ddic.uncertain
                         ))
        FROM diamm_data_itemcomposer AS ddic
                 LEFT JOIN diamm_data_person AS p2 ON ddic.composer_id = p2.id
        WHERE i.id = ddic.item_id)
           AS unattributed_composers,
       (SELECT array_agg(ddg.name)
        FROM diamm_data_composition_genres AS ddcg
                 LEFT JOIN diamm_data_genre AS ddg ON ddcg.genre_id = ddg.id
        WHERE ddcg.composition_id = i.composition_id)
           AS genres,
--        (SELECT array_agg(ddv.id)
--         FROM diamm_data_voice AS ddv
--         WHERE i.id = ddv.item_id)
--            AS voices,
       (SELECT array_agg(ddib.id)
        FROM diamm_data_itembibliography AS ddib
        WHERE i.id = ddib.item_id)
           AS bibliography,
       (SELECT jsonb_agg(jsonb_build_object(
            'type', ddvt.name,
            'text', ddv.voice_text,
            'label', ddv.label,
            'position', ddv.position,
            'clef', ddc.name,
            'mensuration', ddm.sign,
            'standard_text', ddt.text
            ))
        FROM diamm_data_voice AS ddv
        LEFT JOIN diamm_data_voicetype AS ddvt ON ddv.type_id = ddvt.id
        LEFT JOIN diamm_data_clef AS ddc ON ddv.clef_id = ddc.id
        LEFT JOIN diamm_data_mensuration AS ddm ON ddv.mensuration_id = ddm.id
        LEFT JOIN diamm_data_text AS ddt ON ddv.standard_text_id = ddt.id
        WHERE ddv.item_id = i.id)
        AS voices
FROM diamm_data_item AS i
         LEFT JOIN diamm_data_source AS s ON i.source_id = s.id
         LEFT JOIN diamm_data_archive AS a ON s.archive_id = a.id
         LEFT JOIN diamm_data_composition AS c ON i.composition_id = c.id
ORDER BY i.id"""

    return get_db_records(sql_query, cfg)


def _get_item_notes(cfg: dict):
    sql_query = """SELECT n.id AS pk, gen_random_uuid() AS id, 'itemnote' AS record_type,
       n.type AS type,
       COALESCE(
               (
                   (json_build_object(
                           1, 'General Note',
                           2, 'Copying Style',
                           3, 'Concordances',
                           4, 'Layout',
                           5, 'Position on Page',
                           6, 'Non-music contents description',
                           7, 'Indexing or Ordering'
                    )::jsonb)->>(type::integer)::text
                   )::text, ''
       ) AS note_type, n.note AS note
    FROM diamm_data_itemnote AS n
    ORDER BY n.id;"""

    return get_db_records(sql_query, cfg)


def index_items(cfg: dict) -> bool:
    log.info("Indexing items")
    record_groups = _get_items(cfg)
    parallelise(record_groups, record_indexer, create_item_index_documents, cfg)

    notes = _get_item_notes(cfg)
    parallelise(notes, record_indexer, create_item_note_documents, cfg)

    return True


def create_item_index_documents(record, cfg: dict) -> list[dict]:
    return [ItemSearchSerializer(record).data]


def create_item_note_documents(record, cfg: dict) -> list[dict]:
    return [ItemNotesSearchSerializer(record).data]


class ItemNotesSearchSerializer(serpy.DictSerializer):
    pk = serpy.IntField(attr="pk")
    type = serpy.MethodField()

    note_type_i = serpy.IntField(attr="type")
    note_type_s = serpy.MethodField()
    note_sni = serpy.StrField(attr="note")

    def get_note_type_s(self, obj):
        return obj["note_type"]

    def get_type(self, obj):
        return obj["record_type"]


class ItemSearchSerializer(serpy.DictSerializer):
    type = serpy.StrField(attr="type", required=False)
    pk = serpy.IntField(attr="pk", required=False)

    source_i = serpy.IntField(attr="source.pk", required=False)
    source_s = serpy.StrField(attr="source.display_name", required=False)
    pages_ii = serpy.Field(attr="page_ids")
    pages_ssni = serpy.Field(attr="page_numeration")
    composition_s = serpy.StrField(attr="composition_title", required=False)
    composition_i = serpy.IntField(attr="composition", required=False)

    num_voices_s = serpy.StrField(attr="num_voices", required=False)
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
    bibliography_ii = serpy.Field(attr="bibliography")
    voices_json = serpy.MethodField()
    genres_ss = serpy.Field(attr="genres")

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

    def get_composers_ss(self, obj):
        """
        Returns an array of composer names for the purposes of filtering and searching by name.
        """
        ret = []
        if obj.get("anonymous_composition"):
            ret.append("Anonymous")

        composers = process_composers(
            obj.get("composition_composers"), obj.get("unattributed_composers")
        )
        return ret + [c[0] for c in composers]

    def get_composer_ans(self, obj):
        """
        Gets the first composer and stores it in an alphanumeric sort field so that the results may be sorted
        by composer. Esp. useful in non-attributed records.
        """
        composers = process_composers(
            obj.get("composition_composers"), obj.get("unattributed_composers")
        )
        if len(composers) > 0:
            return composers[0][0]
        return "Anonymous"

    def get_voices_json(self, obj):
        if not obj.get("voices"):
            return None

        return obj["voices"]
