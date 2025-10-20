import logging

import ypres

from diamm.serializers.search.helpers import (
    format_person_name,
    get_db_records,
    parallelise,
    record_indexer,
)

log = logging.getLogger("diamm")


def _get_sources(cfg: dict):
    sql_query = """SELECT 'source' AS type, s.id AS pk, s.shelfmark AS shelfmark, s.name AS name,
              concat(a.siglum, ' ', s.shelfmark, coalesce(' (' || s.name || ')', ''))  AS display_name,
              a.name AS archive_name, a.id AS archive_pk, ag.name AS archive_city_name, s.type AS source_type,
              ag2.name AS archive_city_parent_name,
                COALESCE(
                       (
                           (json_build_object(
                                   1, 'Parchment',
                                   2, 'Paper',
                                   3, 'Vellum',
                                   4, 'Wood',
                                   5, 'Slate',
                                   6, 'Mixed Paper and Parchment',
                                   7, 'Other'
                            )::jsonb)->>(surface::integer)::text
                           )::text, ''
               ) AS surface_type,
            s.date_statement AS date_statement, s.measurements AS measurements, s.inventory_provided AS inventory_provided,
            s.start_date AS start_date, s.end_date AS end_date, s.public AS public,
            COALESCE(
               (jsonb_build_object(
                        1, 'Rotulus',
                        2, 'Codex',
                        3, 'Libellus',
                        4, 'Unknown'
                )->>(original_format::integer)::text)::text, ''
            ) AS original_format,
            COALESCE(
               (jsonb_build_object(
                        1, 'Fragment',
                        2, 'Complete',
                        3, 'Lost'
                )->>(current_state::integer)::text)::text, ''
            ) AS current_state,
            COALESCE(
               (jsonb_build_object(
                        1, 'Removed from host manuscript',
                        2, 'Still within host manuscript',
                        3, 'Within fragment collection'
                )->>(current_host::integer)::text)::text, ''
            ) AS current_host,
            COALESCE(
               (jsonb_build_object(
                        1, 'Liturgical book',
                        2, 'Miscellany',
                        3, 'Accounts',
                        4, 'Polyphony',
                        5, 'Songbook',
                        6, 'Other'
                )->>(host_main_contents::integer)::text)::text, ''
            ) AS host_main_contents,
            (SELECT count(itc.id)
                FROM diamm_data_item AS it
                LEFT JOIN diamm_data_composition AS itc ON it.composition_id = itc.id
                WHERE it.composition_id IS NOT NULL AND it.source_id = s.id)
            AS num_compositions,
            (SELECT count(DISTINCT itcc.composer_id)
                FROM diamm_data_item AS it
                LEFT JOIN diamm_data_composition AS itc ON it.composition_id = itc.id
                LEFT JOIN diamm_data_compositioncomposer AS itcc ON itc.id = itcc.composition_id
                WHERE it.composition_id IS NOT NULL and it.source_id = s.id)
            AS num_composers,
           (SELECT json_agg(DISTINCT jsonb_build_object(
                           'last_name', ddp.last_name,
                           'first_name', ddp.first_name,
                           'earliest_year', ddp.earliest_year,
                           'latest_year', ddp.latest_year,
                           'earliest_year_approximate', ddp.earliest_year_approximate,
                           'latest_year_approximate', ddp.latest_year_approximate,
                           'floruit', ddp.floruit
                   ))
                FROM diamm_data_item AS it
                LEFT JOIN diamm_data_composition AS itc ON it.composition_id = itc.id
                LEFT JOIN diamm_data_compositioncomposer AS itcc ON itc.id = itcc.composition_id
                LEFT JOIN diamm_data_person AS ddp ON itcc.composer_id = ddp.id
                WHERE itcc.composition_id IS NOT NULL and it.source_id = s.id)
            AS composers,
            (SELECT array_agg(si.identifier)
                FROM diamm_data_sourceidentifier AS si
                WHERE si.source_id = s.id)
            AS identifiers,
            (SELECT array_agg(ddn.name)
                FROM diamm_data_source_notations AS sn
                LEFT JOIN diamm_data_notation ddn on sn.notation_id = ddn.id
                WHERE sn.source_id = s.id)
            AS notations,
            (SELECT array_agg(ss.set_id)
                FROM diamm_data_set_sources AS ss
                WHERE ss.source_id = s.id)
            AS set_identifiers,
            (SELECT array_agg(CONCAT(ds.id, '|', ds.cluster_shelfmark))
                FROM diamm_data_set_sources AS ss
                LEFT JOIN diamm_data_set ds ON ss.set_id = ds.id
                WHERE ss.source_id = s.id)
            AS set_cluster_shelfmarks,
            (SELECT array_agg(sn.note)
                FROM diamm_data_sourcenote AS sn
                WHERE sn.type != 99 AND sn.source_id = s.id)
            AS notes,
            s.cover_image_id AS cover_image,s.open_images AS open_images,
            (SELECT EXISTS(SELECT ddp.id FROM diamm_data_page AS ddp WHERE ddp.source_id = s.id) AND s.public_images) AS public_images,
            (SELECT EXISTS(SELECT ddu.id FROM diamm_data_sourceurl AS ddu WHERE ddu.source_id = s.id AND ddu.type = 4)) AS has_external_images,
            (SELECT EXISTS(SELECT ddu.id FROM diamm_data_sourceurl AS ddu WHERE ddu.source_id = s.id AND ddu.type = 1)) AS has_external_manifest,
            (SELECT jsonb_agg(jsonb_build_object(
                'primary_study', sb.primary_study,
                'pages', to_jsonb(sb.pages),
                'bibliography', sb.bibliography_id,
                'notes', to_jsonb(sb.notes)
             ))
                FROM diamm_data_sourcebibliography AS sb
                WHERE sb.source_id = s.id)
            AS bibliography
        FROM diamm_data_source AS s
        LEFT JOIN diamm_data_archive AS a ON s.archive_id = a.id
        LEFT JOIN diamm_data_geographicarea AS ag ON a.city_id = ag.id
        LEFT JOIN diamm_data_geographicarea AS ag2 ON ag.parent_id = ag2.id
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
    source_archive_country_s = ypres.StrField(attr="archive_city_parent_name", required=False)
    surface_type_s = ypres.StrField(attr="surface_type", required=False)
    source_type_s = ypres.StrField(attr="source_type", required=False)
    date_statement_s = ypres.StrField(attr="date_statement", required=False)
    measurements_s = ypres.StrField(attr="measurements", required=False)
    inventory_provided_b = ypres.BoolField(attr="inventory_provided", required=False)
    number_of_compositions_i = ypres.IntField(attr="num_compositions", required=False)
    number_of_composers_i = ypres.IntField(attr="num_composers", required=False)
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
        if not obj.get("composers"):
            return None
        return [format_person_name(p) for p in obj["composers"]]

    def get_source_with_images_b(self, obj) -> bool:
        return obj.get("public_images", False) or obj.get(
            "has_external_manifest", False
        )
