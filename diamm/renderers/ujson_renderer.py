import ujson
from rest_framework.renderers import BaseRenderer


class UJSONRenderer(BaseRenderer):
    """
    Renderer which serializes to JSON.
    Applies JSON's backslash-u character escaping for non-ascii characters.
    Uses the blazing-fast ujson library for serialization.

    Adapted from:
    https://github.com/gizmag/drf-ujson-renderer/blob/master/drf_ujson/renderers.py
    """

    media_type = 'application/json'
    format = 'json'
    ensure_ascii = True
    charset = None

    def render(self, data, *args, **kwargs):  # noqa
        if data is None:
            return bytes()

        ret = ujson.dumps(data, ensure_ascii=self.ensure_ascii)

        # force return value to unicode
        if isinstance(ret, str):
            return bytes(ret.encode('utf-8'))

        return ret


class UJSONLDRenderer(UJSONRenderer):
    """
    Renderer that serializes to JSON-LD.
    """
    media_type = 'application/ld+json'