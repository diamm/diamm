import logging

import serpy

from diamm.serializers.search.helpers import (
    get_db_records,
    parallelise,
    record_indexer,
)

log = logging.getLogger("diamm")


def index_archives(cfg: dict) -> bool:
    log.info("Indexing archives")
    record_groups = _get_archives(cfg)
    parallelise(record_groups, record_indexer, create_archive_index_documents, cfg)

    return True


def create_archive_index_documents(record, cfg: dict) -> list[dict]:
    return [ArchiveSearchSerializer(record).data]


def _get_archives(cfg: dict):
    sql_query = """SELECT a.id AS pk, 'archive' AS record_type, a.name AS name, a.siglum AS siglum,
               (SELECT array_agg(concat(a.siglum, ' ', s.shelfmark, coalesce(' (' || s.name || ')', '')))
                    FROM diamm_data_source AS s
                    WHERE s.archive_id = a.id)
                AS sources,
               (SELECT c.name AS name
                    FROM diamm_data_geographicarea AS c
                    WHERE a.city_id = c.id)
                AS "city.name",
               (SELECT c.variant_names
                    FROM diamm_data_geographicarea AS c
                    WHERE a.city_id = c.id)
                AS "city.variant_names",
               (SELECT c2.name
                    FROM diamm_data_geographicarea AS c
                    LEFT JOIN diamm_data_geographicarea AS c2 ON c.parent_id = c2.id
                    WHERE a.city_id = c.id
               ) AS "city.parent.name",
               string_to_array(a.former_sigla, ',') AS former_sigla
        FROM diamm_data_archive AS a
        ORDER BY a.id"""

    return get_db_records(sql_query, cfg)


class ArchiveSearchSerializer(serpy.DictSerializer):
    pk = serpy.IntField()
    type = serpy.StrField(attr="record_type")
    sources_ss = serpy.Field(attr="sources")
    city_s = serpy.StrField(attr="city.name")
    city_variants_ss = serpy.Field(attr="city.variant_names")
    name_s = serpy.StrField(attr="name")
    display_name_ans = serpy.StrField(attr="name")
    country_s = serpy.StrField(attr="city.parent.name", required=False)
    siglum_s = serpy.StrField(attr="siglum")
    former_sigla_ss = serpy.Field(attr="former_sigla")
