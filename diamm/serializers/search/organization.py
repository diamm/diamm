import logging

import ypres

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
    return [OrganizationSearchSerializer(record).serialized]


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
               (SELECT json_agg(otsn.name)
                    FROM diamm_data_organization_subtypes AS ots
                    LEFT JOIN diamm_data_organizationsubtype otsn ON ots.organizationsubtype_id = otsn.id
                    WHERE o.id = ots.organization_id)
               AS organization_subtype,
              string_to_array(o.variant_names, ',') AS variant_names
        FROM diamm_data_organization AS o
        ORDER BY o.id"""

    return get_db_records(sql_query, cfg)


class OrganizationSearchSerializer(ypres.DictSerializer):
    type = ypres.StrField(attr="record_type")
    pk = ypres.IntField()
    public_b = ypres.StaticField(True)
    location_s = ypres.Field(attr="location")

    name_s = ypres.StrField(attr="name")
    display_name_ans = ypres.StrField(attr="name")
    organization_type_s = ypres.StrField(attr="organization_type", required=False)
    organization_subtype_ss = ypres.Field(attr="organization_subtype", required=False)
    variant_names_ss = ypres.MethodField()

    def get_variant_names_ss(self, obj):
        if variants := obj.get("variant_names"):
            return [v.strip() for v in variants]
        return None
