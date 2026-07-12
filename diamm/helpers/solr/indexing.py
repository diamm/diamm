from django.conf import settings

from diamm.helpers.solr.client import DEFAULT_SOLR_CLIENT


def _prepare(instances) -> None:
    for instance in instances:
        fq = [f"type:{instance.__class__.__name__.lower()}", f"pk:{instance.pk}"]
        records = DEFAULT_SOLR_CLIENT.raw_search("*:*", fq=fq, fl="id")
        for document in records.docs:
            DEFAULT_SOLR_CLIENT.delete(
                doc_id=document["id"], core=settings.SOLR["LIVE_CORE"]
            )
            DEFAULT_SOLR_CLIENT.commit(core=settings.SOLR["LIVE_CORE"])


def solr_index(serializer, instance) -> None:
    _prepare([instance])
    data = serializer(instance).data
    DEFAULT_SOLR_CLIENT.index([data], core=settings.SOLR["LIVE_CORE"])
    DEFAULT_SOLR_CLIENT.commit(core=settings.SOLR["LIVE_CORE"])


def solr_index_many(serializer, instances) -> None:
    _prepare(instances)
    data = serializer(instances, many=True).data
    DEFAULT_SOLR_CLIENT.index(data, core=settings.SOLR["LIVE_CORE"])
    DEFAULT_SOLR_CLIENT.commit(core=settings.SOLR["LIVE_CORE"])


def solr_delete(instance) -> None:
    _prepare([instance])


def solr_delete_many(instances: list) -> None:
    _prepare(instances)
