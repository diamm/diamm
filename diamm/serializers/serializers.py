
import serpy


class ContextSerializer(serpy.Serializer):
    """
    Used for serializing database objects, extending the base
    serpy serializer by storing the context arg passed in.

    cf. https://github.com/clarkduvall/serpy/issues/16
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "context" in kwargs:
            self.context = kwargs["context"]

    def __remove_none(self, d: dict) -> dict:
        return {k: v for k, v in d.items() if v is not None}

    def to_value(self, instance: dict | list) -> dict | list:
        """
        Filters out values that have been serialized to 'None' to prevent
        them from being sent to the browser.

        :param instance: A dictionary, or list of dictionaries, to be serialized
        :return: A dictionary or a list of dictionaries with 'None' values filtered out.
        """
        v = super().to_value(instance)

        if self.many:
            return [self.__remove_none(d) for d in v]

        return self.__remove_none(v)


class ContextDictSerializer(serpy.DictSerializer):
    """
    The same as ContextSerializer, but used for serializing dictionaries not
    objects. Useful for serializing Solr results.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "context" in kwargs:
            self.context = kwargs["context"]

    def __remove_none(self, d: dict) -> dict:
        return {k: v for k, v in d.items() if v is not None}

    def to_value(self, instance: dict | list) -> dict | list:
        """
        Filters out values that have been serialized to 'None' to prevent
        them from being sent to the browser.

        :param instance: A dictionary, or list of dictionaries, to be serialized
        :return: A dictionary or a list of dictionaries with 'None' values filtered out.
        """
        v = super().to_value(instance)

        if self.many:
            return [self.__remove_none(d) for d in v]

        return self.__remove_none(v)
