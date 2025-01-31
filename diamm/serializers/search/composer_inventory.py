import logging

import serpy

from diamm.serializers.search.helpers import get_db_records, parallelise, record_indexer

log = logging.getLogger("diamm")


def index_composer_inventory(cfg: dict) -> bool:
    log.info("Indexing composer inventory")
    record_groups = _get_inventory(cfg)
    parallelise(
        record_groups, record_indexer, create_composer_inventory_index_documents, cfg
    )

    return True


def _get_inventory(cfg: dict):
    sql_query = """SELECT it.id AS pk, 'composerinventory' AS record_type, it.id AS item_id,
                       it.source_id AS source_id, cc.uncertain AS uncertain, it.composition_id AS composition_id,
                       cc.composer_id AS composer_id, it.source_attribution AS source_attribution,
                       it.folio_start AS folio_start, it.folio_end AS folio_end,
                       (SELECT concat(c.last_name, coalesce(', ' || c.first_name, ''))
                        FROM diamm_data_person AS c
                        WHERE c.id = cc.composer_id)
                           AS composer,
                       (SELECT co.title
                        FROM diamm_data_composition AS co
                        WHERE co.id = it.composition_id)
                           AS composition
                FROM diamm_data_item AS it
                LEFT JOIN diamm_data_compositioncomposer AS cc ON cc.composition_id = it.composition_id
                ORDER BY it.source_id"""

    return get_db_records(sql_query, cfg)


def create_composer_inventory_index_documents(record, cfg: dict):
    return [ComposerInventorySearchSerializer(record).data]


class ComposerInventorySearchSerializer(serpy.DictSerializer):
    type = serpy.StrField(attr="record_type")
    pk = serpy.IntField()
    composer_s = serpy.MethodField()
    composer_i = serpy.IntField(attr="composer_id", required=False)
    source_i = serpy.IntField(attr="source_id", required=False)
    uncertain_b = serpy.BoolField(attr="uncertain", required=False)
    composition_s = serpy.StrField(attr="composition", required=False)
    composition_i = serpy.IntField(attr="composition_id", required=False)
    folio_start_s = serpy.StrField(attr="folio_start", required=False)
    folio_end_s = serpy.StrField(attr="folio_end", required=False)
    source_attribution_s = serpy.StrField(attr="source_attribution", required=False)
    item_i = serpy.IntField(attr="item_id", required=False)

    def get_composer_s(self, obj):
        if not obj["composer"]:
            return "Anonymous"
        return str(obj["composer"])
