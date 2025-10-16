import logging

import serpy

from diamm.serializers.fields import StaticField
from diamm.serializers.search.helpers import (
    get_db_records,
    parallelise,
    record_indexer,
)

log = logging.getLogger("diamm")


def index_organizations(cfg: dict) -> bool:
    log.info("Indexing organizations")
    record_groups = _get_organizations(cfg)
    parallelise(record_groups, record_indexer, create_organization_index_documents, cfg)

    return True


def create_organization_index_documents(record, cfg: dict):
    return [OrganizationSearchSerializer(record).data]


def _get_organizations(cfg: dict):
    sql_query = """SELECT o.id AS pk, 'organization' AS record_type,
               o.name AS name,
               (SELECT g.name
                    FROM diamm_data_geographicarea AS g
                    WHERE o.location_id = g.id) AS location,
               (SELECT ot.name
                    FROM diamm_data_organizationtype AS ot
                    WHERE o.type_id = ot.id)
                AS organization_type,
              string_to_array(o.variant_names, ',') AS variant_names
        FROM diamm_data_organization AS o
        ORDER BY o.id"""

    return get_db_records(sql_query, cfg)


class OrganizationSearchSerializer(serpy.DictSerializer):
    type = serpy.StrField(attr="record_type")
    pk = serpy.IntField()
    public_b = StaticField(True)
    location_s = serpy.Field(attr="location")

    name_s = serpy.StrField(attr="name")
    display_name_ans = serpy.StrField(attr="name")
    organization_type_s = serpy.StrField(attr="organization_type", required=False)
    variant_names_ss = serpy.MethodField()

    def get_variant_names_ss(self, obj):
        if variants := obj.get("variant_names"):
            return [v.strip() for v in variants]
        return None
