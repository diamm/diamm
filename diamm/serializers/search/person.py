import logging

import serpy
import ujson

from diamm.serializers.fields import StaticField
from diamm.serializers.search.helpers import (
    format_person_name,
    get_db_records,
    parallelise,
    record_indexer,
)

log = logging.getLogger("diamm")


def index_people(cfg: dict) -> bool:
    log.info("Indexing people")
    record_groups = _get_people(cfg)
    parallelise(record_groups, record_indexer, create_person_index_documents, cfg)

    return True


def create_person_index_documents(record, cfg: dict) -> list[dict]:
    return [PersonSearchSerializer(record).data]


def _get_people(cfg: dict):
    sql_query = """SELECT p.id AS pk, 'person' AS record_type,
                   jsonb_build_object(
                           'id', p.id,
                           'last_name', p.last_name,
                           'first_name', p.first_name,
                           'earliest_year', p.earliest_year,
                           'latest_year', p.latest_year,
                           'earliest_year_approximate', p.earliest_year_approximate,
                           'latest_year_approximate', p.latest_year_approximate,
                           'floruit', p.floruit) AS full_name_info,
                    p.last_name AS last_name, p.first_name AS first_name,
                    p.title AS title, p.earliest_year AS earlist_year, p.latest_year AS latest_year,
                    (SELECT array_agg(DISTINCT r.name)
                     FROM diamm_data_personrole AS pr
                     LEFT JOIN diamm_data_role AS r ON pr.role_id = r.id
                     WHERE pr.person_id = p.id) AS roles,
                    (SELECT array_agg(n.note)
                     FROM diamm_data_personnote AS n
                     WHERE n.person_id = p.id AND n.type = 2) AS variant_names,
                    (SELECT array_agg(DISTINCT c.title)
                     FROM diamm_data_compositioncomposer AS cc
                     LEFT JOIN diamm_data_composition AS c ON c.id = cc.composition_id
                     WHERE p.id = cc.composer_id) AS compositions
            FROM diamm_data_person AS p
            ORDER BY p.id"""

    return get_db_records(sql_query, cfg)


class PersonSearchSerializer(serpy.DictSerializer):
    pk = serpy.IntField()
    type = serpy.StrField(attr="record_type")
    name_s = serpy.MethodField(method="names")
    public_b = StaticField(True)
    # Copy the full name to a sorting field
    display_name_ans = serpy.MethodField(method="names")
    last_name_s = serpy.StrField(attr="last_name")
    first_name_s = serpy.StrField(attr="first_name", required=False)
    title_s = serpy.StrField(attr="title", required=False)
    role_ss = serpy.Field(attr="roles")
    start_date_i = serpy.IntField(attr="earliest_year", required=False)
    end_date_i = serpy.IntField(attr="latest_year", required=False)
    variant_names_ss = serpy.MethodField()
    compositions_ss = serpy.Field(attr="compositions")

    def get_variant_names_ss(self, obj) -> list | None:
        if variant_names := obj.get("variant_names"):
            return [
                name.strip() for names in variant_names for name in names.split(";")
            ]
        return None

    def names(self, obj):
        ndata = ujson.loads(obj["full_name_info"])
        return format_person_name(ndata)
