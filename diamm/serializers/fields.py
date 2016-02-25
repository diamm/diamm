import serpy


class StaticField(serpy.Field):
    def __init__(self, value, *args, **kwargs):
        super(StaticField, self).__init__(*args, **kwargs)
        self.value = value

    def to_value(self, value):
        return self.value

    def as_getter(self, serializer_field_name, serializer_cls):
        return self.to_value
