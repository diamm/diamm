import scorched
from django.conf import settings


def solr_index(serializer, instance):
    connection = scorched.SolrInterface(settings.SOLR['SERVER'])
    serialized = serializer(instance)
    data = serialized.data
    q = {'type': data['type'], 'pk': instance.pk}
    records = connection.query(**q).execute()
    if records:
        print("Found records to delete: {0}".format(" ".join([x['type'] for x in records])))
        connection.delete_by_ids([x['id'] for x in records])
        connection.commit()

    connection.add(data)
    connection.commit()


def solr_delete(serializer, instance):
    connection = scorched.SolrInterface(settings.SOLR['SERVER'])
    serialized = serializer(instance)
    data = serialized.data
    q = {'type': data['type'], 'pk': instance.pk}
    records = connection.query(**q).execute()
    if records:
        connection.delete_by_ids([x['id'] for x in records])
        connection.commit()

