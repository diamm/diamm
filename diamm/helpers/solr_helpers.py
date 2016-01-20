import scorched
import scorched.search
import operator
from django.conf import settings


def build_query(querytext):
    """
        Takes a query text with boolean operators AND, OR, and NOT and
            converts it to an array containing operator objects.
    :param querytext: String, "Foo AND Bar NOT Baz"
    :return: List of operatorized parameters
    """
    Q = scorched.search.LuceneQuery
    qcomponents = querytext.split(" ")
    q = []
    for word in qcomponents:
        word = word.strip().lower()
        if word == 'and':
            q.append(operator.and_)
        elif word == 'or':
            q.append(operator.or_)
        elif word == 'not':
            q.append(operator.and_)
            q.append(operator.not_)
        else:
            q.append(Q(word))
    return q


def solr_index(serializer, instance):
    connection = scorched.SolrInterface(settings.SOLR['SERVER'])
    serialized = serializer(instance)
    data = serialized.data
    q = {'type': data['type'], 'pk': instance.pk}
    records = connection.query(**q).execute()
    if records:
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

