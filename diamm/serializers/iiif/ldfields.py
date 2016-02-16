import serpy


class LDKeywordField(serpy.Field):
    def __init__(self, label=None, **kwargs):
        super(LDKeywordField, self).__init__(**kwargs)
        self.label = label
