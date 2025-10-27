import copy
import logging

import ujson
import ypres

from diamm.serializers.search.helpers import (
    get_db_records,
    parallelise,
    process_composers,
    record_indexer, process_bibliography_entries, update_db_records,
)

log = logging.getLogger("diamm")


def _get_items(cfg: dict):
    sql_query = """WITH
-- pages per item
item_pages AS (
    SELECT
        ddip.item_id,
        array_agg(ddip.page_id ORDER BY ddip.page_id) AS page_ids,
        array_agg(CONCAT(p.id, '|', p.numeration) ORDER BY p.id) AS page_numeration
    FROM diamm_data_item_pages ddip
        JOIN diamm_data_page p ON p.id = ddip.page_id
    GROUP BY ddip.item_id
),

-- composers from composition
composition_composers AS (
    SELECT
        cc2.composition_id,
        jsonb_agg(
                jsonb_build_object(
                        'id', p2.id,
                        'last_name', p2.last_name,
                        'first_name', p2.first_name,
                        'earliest_year', p2.earliest_year,
                        'latest_year', p2.latest_year,
                        'earliest_year_approximate', p2.earliest_year_approximate,
                        'latest_year_approximate', p2.latest_year_approximate,
                        'floruit', p2.floruit,
                        'uncertain', cc2.uncertain
                )
                ORDER BY coalesce(p2.last_name,''), coalesce(p2.first_name,'')
        ) AS json
    FROM diamm_data_compositioncomposer cc2
        JOIN diamm_data_person p2 ON p2.id = cc2.composer_id
    GROUP BY cc2.composition_id
),

-- unattributed composers per item
item_unattributed_composers AS (
    SELECT
        ddic.item_id,
        jsonb_agg(
                jsonb_build_object(
                        'id', p2.id,
                        'last_name', p2.last_name,
                        'first_name', p2.first_name,
                        'earliest_year', p2.earliest_year,
                        'latest_year', p2.latest_year,
                        'earliest_year_approximate', p2.earliest_year_approximate,
                        'latest_year_approximate', p2.latest_year_approximate,
                        'floruit', p2.floruit,
                        'uncertain', ddic.uncertain
                )
                ORDER BY coalesce(p2.last_name,''), coalesce(p2.first_name,'')
        ) AS json
    FROM diamm_data_itemcomposer ddic
        JOIN diamm_data_person p2 ON p2.id = ddic.composer_id
    GROUP BY ddic.item_id
),

-- genres per composition
composition_genres AS (
    SELECT
        ddcg.composition_id,
        array_agg(ddg.name ORDER BY ddg.name) AS genres
    FROM diamm_data_composition_genres ddcg
        JOIN diamm_data_genre ddg ON ddg.id = ddcg.genre_id
    GROUP BY ddcg.composition_id
),

-- voices per item
item_voices AS (
    SELECT
        ddv.item_id,
        jsonb_agg(
                jsonb_build_object(
                        'type', ddvt.name,
                        'text', ddv.voice_text,
                        'label', ddv.label,
                        'position', ddv.position,
                        'clef', ddc.name,
                        'mensuration', ddm.sign,
                        'standard_text', ddt.text
                )
                ORDER BY ddv.position
        ) AS json
    FROM diamm_data_voice ddv
        LEFT JOIN diamm_data_voicetype ddvt ON ddvt.id = ddv.type_id
        LEFT JOIN diamm_data_clef ddc ON ddc.id = ddv.clef_id
        LEFT JOIN diamm_data_mensuration ddm ON ddm.id = ddv.mensuration_id
        LEFT JOIN diamm_data_text ddt ON ddt.id = ddv.standard_text_id
    GROUP BY ddv.item_id
),

-- bibliography helpers
bib_people AS (
    SELECT
        bar1.bibliography_entry_id AS bib_id,
        jsonb_agg(
                jsonb_build_object(
                        'id', bau1.id,
                        'last_name', bau1.last_name,
                        'first_name', bau1.first_name,
                        'role', bar1.role,
                        'position', bar1.position
                )
                ORDER BY bar1.position NULLS LAST, coalesce(bau1.last_name,''), coalesce(bau1.first_name,'')
        ) AS people
    FROM diamm_data_bibliographyauthorrole bar1
        JOIN diamm_data_bibliographyauthor bau1 ON bau1.id = bar1.bibliography_author_id
    GROUP BY bar1.bibliography_entry_id
),

bib_publications AS (
    SELECT
        bpu1.bibliography_id AS bib_id,
        jsonb_agg(
                jsonb_build_object(
                        'id', bpu1.id,
                        'type', bpu1.type,
                        'entry', bpu1.entry
                )
                ORDER BY bpu1.id
        ) AS publications
    FROM diamm_data_bibliographypublication bpu1
    GROUP BY bpu1.bibliography_id
),

-- item ↔ bibliography links + per-bib JSON
item_bib_rows AS (
    SELECT
        ddb.item_id,
        jsonb_agg(
                jsonb_build_object(
                        'title', bib.title,
                        'type', bib.type_id,
                        'year', bib.year,
                        'people', bp.people,
                        'publication', bpub.publications,
                        'pages', ddb.pages,
                        'notes', ddb.notes
                )
                ORDER BY bib.id
        ) AS item_bibliography
    FROM diamm_data_itembibliography ddb
        JOIN diamm_data_bibliography bib ON bib.id = ddb.bibliography_id
        LEFT JOIN bib_people bp ON bp.bib_id = bib.id
        LEFT JOIN bib_publications bpub ON bpub.bib_id = bib.id
    GROUP BY ddb.item_id
),

-- bare bibliography id list if you still need it
item_bib_ids AS (
    SELECT item_id, array_agg(ddb.id ORDER BY ddb.id) AS bibliography
    FROM diamm_data_itembibliography ddb
    GROUP BY item_id
)

                   SELECT
                       'item' AS type,
                       i.id AS pk,
                       i.source_id AS "source.pk",
                       concat(a.siglum, ' ', s.shelfmark, coalesce(' (' || s.name || ')', '')) AS "source.display_name",

                       ip.page_ids,
                       ip.page_numeration,

                       i.num_voices,
                       i.item_title,
                       i.source_attribution,
                       NULLIF(i.source_incipit, '') AS source_incipit,
                       i.source_order,
                       i.folio_start,
                       i.folio_end,

                       i.composition_id AS composition,
                       c.title AS composition_title,
                       c.anonymous AS anonymous_composition,

                       cc.json AS composition_composers,
                       iuc.json AS unattributed_composers,
                       cg.genres,

                       ibids.bibliography,
                       iv.json AS voices,
                       ibr.item_bibliography

                   FROM diamm_data_item i
                       LEFT JOIN diamm_data_source s ON s.id = i.source_id
                       LEFT JOIN diamm_data_archive a ON a.id = s.archive_id
                       LEFT JOIN diamm_data_composition c ON c.id = i.composition_id

                       LEFT JOIN item_pages ip ON ip.item_id = i.id
                       LEFT JOIN composition_composers cc ON cc.composition_id = i.composition_id
                       LEFT JOIN item_unattributed_composers iuc ON iuc.item_id = i.id
                       LEFT JOIN composition_genres cg ON cg.composition_id = i.composition_id
                       LEFT JOIN item_bib_ids ibids ON ibids.item_id = i.id
                       LEFT JOIN item_bib_rows ibr ON ibr.item_id = i.id
                       LEFT JOIN item_voices iv ON iv.item_id = i.id

                   ORDER BY i.id;"""

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


def index_bibliography_in_database(record, cfg: dict) -> bool:
    log.info("Updating bibliograpy entries in item record.")
    item_id = record["pk"]

    item_bibliography = record.get("item_bibliography")
    if not item_bibliography:
        return False

    list_of_entries = ujson.loads(item_bibliography)
    processed_entries = [process_bibliography_entries(u) for u in list_of_entries if u]
    processed_str = ujson.dumps(processed_entries)

    sql_query = f"""UPDATE diamm_data_item AS i SET bibliography_json = %s WHERE i.id = %s"""
    update_db_records(sql_query, (processed_str, item_id), cfg)

    return True


def create_item_index_documents(record, cfg: dict) -> list[dict]:
    # Cache the item bibliography in the database so that we don't have to also hit Solr
    # for every item in an inventory, we can just pull the JSON representation from the
    # database.
    success = index_bibliography_in_database(copy.deepcopy(record), cfg)
    return [ItemSearchSerializer(record).serialized]


def create_item_note_documents(record, cfg: dict) -> list[dict]:
    return [ItemNotesSearchSerializer(record).serialized]


class ItemNotesSearchSerializer(ypres.DictSerializer):
    pk = ypres.IntField(attr="pk")
    type = ypres.MethodField()

    note_type_i = ypres.IntField(attr="type")
    note_type_s = ypres.MethodField()
    note_sni = ypres.StrField(attr="note")

    def get_note_type_s(self, obj):
        return obj["note_type"]

    def get_type(self, obj):
        return obj["record_type"]


class ItemSearchSerializer(ypres.DictSerializer):
    type = ypres.StrField(attr="type", required=False)
    pk = ypres.IntField(attr="pk", required=False)

    source_i = ypres.IntField(attr="source.pk", required=False)
    source_s = ypres.StrField(attr="source.display_name", required=False)
    pages_ii = ypres.Field(attr="page_ids")
    pages_ssni = ypres.Field(attr="page_numeration")
    composition_s = ypres.StrField(attr="composition_title", required=False)
    composition_i = ypres.IntField(attr="composition", required=False)

    num_voices_s = ypres.StrField(attr="num_voices", required=False)
    item_title_s = ypres.StrField(attr="item_title", required=False)
    source_attribution_s = ypres.StrField(attr="source_attribution", required=False)
    source_incipit_s = ypres.StrField(attr="source_incipit", required=False)
    source_order_f = ypres.FloatField(attr="source_order", required=False)

    folio_start_s = ypres.StrField(attr="folio_start", required=False)
    folio_end_s = ypres.StrField(attr="folio_end", required=False)
    folio_start_ans = ypres.StrField(attr="folio_start", required=False)
    folio_end_ans = ypres.StrField(attr="folio_end", required=False)
    composers_ssni = ypres.MethodField()
    composers_ss = ypres.MethodField()
    composer_ans = ypres.MethodField()
    bibliography_ii = ypres.Field(attr="bibliography")
    voices_json = ypres.MethodField()
    genres_ss = ypres.Field(attr="genres")

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
