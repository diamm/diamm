import logging

import ujson
import ypres

from diamm.serializers.search.helpers import (
    format_person_name,
    get_db_records,
    parallelise,
    record_indexer,
)

log = logging.getLogger("diamm")


def _get_sources(cfg: dict):
    sql_query = """WITH src AS (
        SELECT
            s.*,
            a.siglum,
            a.name  AS archive_name,
            a.id    AS archive_pk,
            ag.name AS archive_city_name,
            ag2.name AS archive_city_parent_name
        FROM diamm_data_source s
            LEFT JOIN diamm_data_archive a ON s.archive_id = a.id
            LEFT JOIN diamm_data_geographicarea ag  ON a.city_id   = ag.id
            LEFT JOIN diamm_data_geographicarea ag2 ON ag.parent_id = ag2.id
    ),

-- items + compositions + composition-composers aggregated once
agg_items AS (
        SELECT
            it.source_id,
            COUNT(itc.id) FILTER (WHERE it.composition_id IS NOT NULL) AS num_compositions,
            COUNT(itc.id) FILTER (WHERE itc.anonymous IS FALSE) AS num_attributed_compositions,
            COUNT(DISTINCT itcc.composer_id) AS num_composers,
            COUNT(itc.id) FILTER (WHERE itc.anonymous IS TRUE) as num_anonymous_compositions,
            JSONB_AGG(DISTINCT JSONB_BUILD_OBJECT(
                    'last_name', ddp.last_name,
                    'first_name', ddp.first_name,
                    'earliest_year', ddp.earliest_year,
                    'latest_year', ddp.latest_year,
                    'earliest_year_approximate', ddp.earliest_year_approximate,
                    'latest_year_approximate', ddp.latest_year_approximate,
                    'floruit', ddp.floruit
            )) FILTER (WHERE itcc.composition_id IS NOT NULL)
                AS composers
        FROM diamm_data_item it
            LEFT JOIN diamm_data_composition itc        ON it.composition_id = itc.id
            LEFT JOIN diamm_data_compositioncomposer itcc ON itc.id = itcc.composition_id
            LEFT JOIN diamm_data_person ddp             ON itcc.composer_id = ddp.id
        GROUP BY it.source_id
),

-- uninventoried composers path
agg_uninv_composers AS (
        SELECT
            it.source_id,
            COUNT(DISTINCT iic.composer_id) AS num_uninventoried_composers,
            JSONB_AGG(DISTINCT JSONB_BUILD_OBJECT(
                    'last_name', p.last_name,
                    'first_name', p.first_name,
                    'earliest_year', p.earliest_year,
                    'latest_year', p.latest_year,
                    'earliest_year_approximate', p.earliest_year_approximate,
                    'latest_year_approximate', p.latest_year_approximate,
                    'floruit', p.floruit
        )) AS uninventoried_composers
        FROM diamm_data_item it
            JOIN diamm_data_itemcomposer iic ON iic.item_id = it.id
            JOIN diamm_data_person p         ON p.id = iic.composer_id
        GROUP BY it.source_id
),

agg_identifiers AS (
        SELECT source_id, ARRAY_AGG(identifier) AS identifiers
        FROM diamm_data_sourceidentifier
        GROUP BY source_id
),

agg_notations AS (
        SELECT sn.source_id, ARRAY_AGG(n.name) AS notations
        FROM diamm_data_source_notations sn
            LEFT JOIN diamm_data_notation n ON n.id = sn.notation_id
        GROUP BY sn.source_id
),

agg_sets AS (
        SELECT
            ss.source_id,
            ARRAY_AGG(ss.set_id)                                             AS set_identifiers,
            ARRAY_AGG(CONCAT(ds.id, '|', ds.cluster_shelfmark))              AS set_cluster_shelfmarks
        FROM diamm_data_set_sources ss
            LEFT JOIN diamm_data_set ds ON ds.id = ss.set_id
        GROUP BY ss.source_id
),

agg_notes AS (
        SELECT source_id, ARRAY_AGG(sn.note) AS notes
        FROM diamm_data_sourcenote sn
        WHERE sn.type <> 99
        GROUP BY source_id
),

agg_pages AS (
        SELECT source_id, TRUE AS has_pages
        FROM diamm_data_page
        GROUP BY source_id
),

agg_urls AS (
        SELECT
            source_id,
            BOOL_OR(type = 4) AS has_external_images,
            BOOL_OR(type = 1) AS has_external_manifest
        FROM diamm_data_sourceurl
        GROUP BY source_id
),

agg_biblio AS (
        SELECT
            sb.source_id,
            JSONB_AGG(JSONB_BUILD_OBJECT(
                    'primary_study', sb.primary_study,
                    'pages',         TO_JSONB(sb.pages),
                    'bibliography',  sb.bibliography_id,
                    'notes',         TO_JSONB(sb.notes)
                      )) AS bibliography
        FROM diamm_data_sourcebibliography sb
        GROUP BY sb.source_id
)

SELECT
   'source' AS type,
   s.id AS pk,
   s.shelfmark,
   s.name,
   CONCAT_WS(
           ' ',
           s.siglum,
           s.shelfmark,
           NULLIF('(' || s.name || ')', '()')
   ) AS display_name,
   s.archive_name,
   s.archive_pk,
   s.archive_city_name,
   s.type AS source_type,
   s.archive_city_parent_name,

   /* enum lookups -> CASE (faster & clearer than json lookups) */
   COALESCE(
           CASE s.surface
               WHEN 1 THEN 'Parchment'
               WHEN 2 THEN 'Paper'
               WHEN 3 THEN 'Vellum'
               WHEN 4 THEN 'Wood'
               WHEN 5 THEN 'Slate'
               WHEN 6 THEN 'Mixed Paper and Parchment'
               WHEN 7 THEN 'Other'
               END, ''
   ) AS surface_type,

   s.date_statement,
   s.measurements,
   s.inventory_provided,
   s.start_date,
   s.end_date,
   s.public,

   COALESCE(
           CASE s.original_format
               WHEN 1 THEN 'Rotulus'
               WHEN 2 THEN 'Codex'
               WHEN 3 THEN 'Libellus'
               WHEN 4 THEN 'Unknown'
               END, ''
   ) AS original_format,

   COALESCE(
           CASE s.current_state
               WHEN 1 THEN 'Fragment'
               WHEN 2 THEN 'Complete'
               WHEN 3 THEN 'Lost'
               END, ''
   ) AS current_state,

   COALESCE(
           CASE s.current_host
               WHEN 1 THEN 'Removed from host manuscript'
               WHEN 2 THEN 'Still within host manuscript'
               WHEN 3 THEN 'Within fragment collection'
               END, ''
   ) AS current_host,

   COALESCE(
           CASE s.host_main_contents
               WHEN 1 THEN 'Liturgical book'
               WHEN 2 THEN 'Miscellany'
               WHEN 3 THEN 'Accounts'
               WHEN 4 THEN 'Polyphony'
               WHEN 5 THEN 'Songbook'
               WHEN 6 THEN 'Other'
               END, ''
   ) AS host_main_contents,

   ai.num_compositions,
   ai.num_composers,
   ai.composers,
   ai.num_anonymous_compositions,
   ai.num_attributed_compositions,
   auc.uninventoried_composers,
   auc.num_uninventoried_composers,
   idt.identifiers,
   nt.notations,
   st.set_identifiers,
   st.set_cluster_shelfmarks,
   nt2.notes,

   s.cover_image_id AS cover_image,
   s.open_images AS open_images,

   /* public_images: has pages AND source says public */
   (COALESCE(pg.has_pages, FALSE) AND s.public_images) AS public_images,

   COALESCE(u.has_external_images,  FALSE) AS has_external_images,
   COALESCE(u.has_external_manifest, FALSE) AS has_external_manifest,

   bib.bibliography

FROM src s
   LEFT JOIN agg_items            ai  ON ai.source_id  = s.id
   LEFT JOIN agg_uninv_composers  auc ON auc.source_id = s.id
   LEFT JOIN agg_identifiers      idt ON idt.source_id = s.id
   LEFT JOIN agg_notations        nt  ON nt.source_id  = s.id
   LEFT JOIN agg_sets             st  ON st.source_id  = s.id
   LEFT JOIN agg_notes            nt2 ON nt2.source_id = s.id
   LEFT JOIN agg_pages            pg  ON pg.source_id  = s.id
   LEFT JOIN agg_urls             u   ON u.source_id   = s.id
   LEFT JOIN agg_biblio           bib ON bib.source_id = s.id
ORDER BY s.id;"""

    return get_db_records(sql_query, cfg)


def index_sources(cfg: dict) -> bool:
    log.info("Indexing sources")
    record_groups = _get_sources(cfg)
    parallelise(record_groups, record_indexer, create_source_index_documents, cfg)

    return True


def create_source_index_documents(record, cfg: dict) -> list[dict]:
    return [SourceSearchSerializer(record).serialized]


class SourceSearchSerializer(ypres.DictSerializer):
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

    type = ypres.StrField(attr="type")
    pk = ypres.IntField()

    shelfmark_s = ypres.StrField(attr="shelfmark", required=False)
    name_s = ypres.StrField(attr="name", required=False)
    display_name_s = ypres.StrField(attr="display_name", required=False)
    archive_s = ypres.StrField(attr="archive_name", required=False)
    archive_i = ypres.IntField(attr="archive_pk", required=False)
    source_archive_city_s = ypres.StrField(attr="archive_city_name", required=False)
    source_archive_country_s = ypres.StrField(
        attr="archive_city_parent_name", required=False
    )
    surface_type_s = ypres.StrField(attr="surface_type", required=False)
    source_type_s = ypres.StrField(attr="source_type", required=False)
    date_statement_s = ypres.StrField(attr="date_statement", required=False)
    measurements_s = ypres.StrField(attr="measurements", required=False)
    inventory_provided_b = ypres.BoolField(attr="inventory_provided", required=False)
    number_of_compositions_i = ypres.IntField(attr="num_compositions", required=False)
    number_of_attributed_compositions_i = ypres.IntField(
        attr="num_attributed_compositions", required=False
    )
    number_of_composers_i = ypres.IntField(attr="num_composers", required=False)
    number_of_anonymous_compositions_i = ypres.IntField(
        attr="num_anonymous_compositions", required=False
    )
    number_of_uninventoried_composers_i = ypres.IntField(
        attr="num_uninventoried_composers", required=False
    )
    source_composers_ss = ypres.MethodField()

    identifiers_ss = ypres.Field(attr="identifiers")
    notations_ss = ypres.Field(attr="notations")

    sets_ii = ypres.Field(attr="set_identifiers")
    sets_ssni = ypres.Field(attr="set_cluster_shelfmarks")
    notes_txt = ypres.Field(attr="notes")

    start_date_i = ypres.IntField(attr="start_date", required=False)
    end_date_i = ypres.IntField(attr="end_date", required=False)
    cover_image_i = ypres.IntField(attr="cover_image", required=False)
    public_images_b = ypres.BoolField(attr="public_images", required=False)
    public_b = ypres.BoolField(attr="public", required=False)
    open_images_b = ypres.BoolField(attr="open_images", required=False)
    external_images_b = ypres.BoolField(attr="has_external_images", required=False)
    external_manifest_b = ypres.BoolField(attr="has_external_manifest", required=False)
    bibliography_json = ypres.Field(attr="bibliography")
    source_with_images_b = ypres.MethodField()

    original_format_s = ypres.StrField(attr="original_format", required=False)
    current_state_s = ypres.StrField(attr="current_state", required=False)
    current_host_s = ypres.StrField(attr="current_host", required=False)
    host_main_contents_s = ypres.StrField(attr="host_main_contents", required=False)

    def get_source_composers_ss(self, obj) -> list | None:
        if obj.get("composers"):
            p_composers: list[dict] = ujson.loads(obj["composers"])
            inventoried: list = [format_person_name(p) for p in p_composers]
        else:
            inventoried = []

        if obj.get("uninventoried_composers"):
            p_uninv: list[dict] = ujson.loads(obj["uninventoried_composers"])
            uninventoried: list = [format_person_name(p) for p in p_uninv]
        else:
            uninventoried = []

        return (inventoried + uninventoried) or None

    def get_source_with_images_b(self, obj) -> bool:
        return obj.get("public_images", False) or obj.get(
            "has_external_manifest", False
        )
