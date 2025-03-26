from datetime import date, datetime, time

import serpy  # type: ignore


class StaticField(serpy.Field):
    def __init__(self, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = value

    def to_value(self, value):
        return self.value

    def as_getter(self, serializer_field_name, serializer_cls):
        return self.to_value


# From https://github.com/PKharlamov/drf-serpy/blob/master/drf_serpy/fields.py
class DateField(serpy.Field):
    """A `Field` that converts the value to a date format."""

    date_format = "%Y-%m-%d"

    def __init__(self, date_format: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.date_format = date_format or self.date_format

    def to_value(self, value: datetime | time | date) -> str | None:
        if value:
            return value.strftime(self.date_format)
        return None


class DateTimeField(DateField):
    """A `Field` that converts the value to a date time format."""

    date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
