import pysolr
from django.conf import settings


def __solr_prepare(instances):
    """
        Both index and delete require the step of checking
        to see if the requested documents exist. For indexing, this is so we don't get
        duplicate records in the index; for deleting, it's rather obvious.
        This method deletes the documents in question and returns the connection object.

        If further action is required (i.e., actually indexing) the calling method
        can re-use the connection object to do this.

        An array of model instances must be passed to this method. For single instances,
        the caller should wrap it in an array of length 1 before passing it in.
    """
    connection = pysolr.Solr(settings.SOLR['SERVER'])
    for instance in instances:
        fq = ["type:{0}".format(instance.__class__.__name__.lower()),
              "pk:{0}".format(instance.pk)]
        records = connection.search("*:*", fq=fq, fl="id")
        if records.docs:
            for doc in records.docs:
                connection.delete(id=doc['id'])

    return connection


def solr_index(serializer, instance):
    connection = __solr_prepare([instance])
    serialized = serializer(instance)
    data = serialized.data

    # pysolr add takes a list of documents, so we wrap the instance in an array.
    connection.add([data])
    connection.commit()


def solr_index_many(serializer, instances):
    connection = __solr_prepare(instances)
    serialized = serializer(instances, many=True)
    data = serialized.data
    connection.add(data)
    connection.commit()


def solr_delete(serializer, instance):
    __solr_prepare([instance])


def solr_delete_many(serializer, instances):
    __solr_prepare(instances)
