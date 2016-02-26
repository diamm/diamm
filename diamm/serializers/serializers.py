import serpy


class ContextSerializer(serpy.Serializer):
    def __init__(self, *args, **kwargs):
        super(ContextSerializer, self).__init__(*args, **kwargs)
        if 'context' in kwargs:
            self.context = kwargs['context']


class ContextDictSerializer(serpy.DictSerializer):
    def __init__(self, *args, **kwargs):
        super(ContextDictSerializer, self).__init__(*args, **kwargs)
        if 'context' in kwargs:
            self.context = kwargs['context']
