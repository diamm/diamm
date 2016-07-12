import serpy
from rest_framework.reverse import reverse

class ContextSerializer(serpy.Serializer):
    """
        Used for serializing database objects, extending the base
        serpy serializer by storing the context arg passed in.

        cf. https://github.com/clarkduvall/serpy/issues/16
    """
    def __init__(self, *args, **kwargs):
        super(ContextSerializer, self).__init__(*args, **kwargs)
        if 'context' in kwargs:
            self.context = kwargs['context']


class ContextDictSerializer(serpy.DictSerializer):
    """
        The same as ContextSerializer, but used for serializing dictionaries not
        objects. Useful for serializing Solr results.
    """
    def __init__(self, *args, **kwargs):
        super(ContextDictSerializer, self).__init__(*args, **kwargs)
        if 'context' in kwargs:
            self.context = kwargs['context']

class HyperlinkedContextSerializer(ContextSerializer):
    """
        Provides a method for getting the models related url
    """
    def __init__(self, *args, **kwargs):
        super(HyperlinkedContextSerializer, self).__init__(*args, **kwargs)
        if 'context' in kwargs:
            self.context = kwargs['context']

    def generate_url(self, view_name, *args, **kwargs):
        return self.context['request'].build_absolute_uri(reverse(view_name, args, kwargs))

