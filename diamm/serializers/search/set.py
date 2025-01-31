import functools
import logging
from typing import Optional

import serpy
import ujson

from diamm.serializers.search.helpers import get_db_records, parallelise, record_indexer

log = logging.getLogger("diamm")


def index_sets(cfg: dict) -> bool:
    log.info("Indexing sets")
    record_groups = _get_sets(cfg)
    parallelise(record_groups, record_indexer, create_set_index_documents, cfg)

    return True


def _get_sets(cfg):
    sql_query = """SELECT s.id AS pk, 'set' AS record_type, s.cluster_shelfmark AS cluster_shelfmark,
                   (SELECT array_agg(ss.source_id ORDER BY ss.source_id)
                        FROM diamm_data_set_sources AS ss
                        WHERE ss.set_id = s.id) AS sources,
                   (SELECT jsonb_agg(DISTINCT jsonb_build_object(
                                              'name', a.name,
                                              'siglum', a.siglum,
                                              'city', c.name
                                              ))
                        FROM diamm_data_set_sources AS ss
                        LEFT JOIN diamm_data_source AS so ON ss.source_id = so.id
                        LEFT JOIN diamm_data_archive AS a ON so.archive_id = a.id
                        LEFT JOIN diamm_data_geographicarea AS c ON a.city_id = c.id
                        WHERE ss.set_id = s.id) AS archives,
                   COALESCE(((json_build_object(
                                       1, 'Partbooks',
                                       2, 'Fragments of a whole',
                                       3, 'Linked by Origin or Contents',
                                       4, 'Non-music Collection',
                                       5, 'Copyist or Scribal Concordance',
                                       6, 'Source bound in separate volumes',
                                       7, 'Project Collection'
                                )::jsonb)->>(s.type::integer)::text
                               )::text, ''
                   ) AS set_type
            FROM diamm_data_set AS s
            ORDER BY s.id"""

    return get_db_records(sql_query, cfg)


def create_set_index_documents(record, cfg: dict):
    return [SetSearchSerializer(record).data]


class SetSearchSerializer(serpy.DictSerializer):
    type = serpy.StrField(attr="record_type")
    pk = serpy.IntField()
    cluster_shelfmark_s = serpy.StrField(attr="cluster_shelfmark")

    # allow sorting by alpha-numeric shelfmark.
    cluster_shelfmark_ans = serpy.StrField(attr="cluster_shelfmark")
    display_name_ans = serpy.StrField(attr="cluster_shelfmark")

    sources_ii = serpy.Field(attr="sources")
    set_type_s = serpy.StrField(attr="set_type")
    archives_ss = serpy.MethodField()
    archives_cities_ss = serpy.MethodField()

    # add archive names to sets so that people can search for "partbooks oxford" or "trinity college partbooks"
    def get_archives_ss(self, obj) -> Optional[list]:
        archives = process_archives(obj["archives"]) if obj.get("archives") else []
        return [f"{a['siglum']} {a['name']} {a['city']}" for a in archives]

    # add archive cities so that people can search for e.g., 'london partbooks' or 'cambridge partbooks'
    def get_archives_cities_ss(self, obj) -> Optional[list]:
        archives = process_archives(obj["archives"]) if obj.get("archives") else []
        return [f"{a['city']}" for a in archives]


@functools.lru_cache
def process_archives(archive_str: Optional[str]) -> Optional[list]:
    return ujson.loads(archive_str) if archive_str else None
