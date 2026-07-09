from collections.abc import Iterable

from django.utils.html import format_html, format_html_join
from django.utils.safestring import SafeString


def admin_change_link(url: str, label: object) -> SafeString:
    return format_html('<a href="{}">{}</a>', url, label)


def html_join(values: Iterable[object]) -> SafeString | str:
    values = list(values)
    if not values:
        return ""

    separator = format_html("{}<br />", "; ")
    rows = [("", values[0])]
    rows.extend((separator, value) for value in values[1:])
    return format_html_join("", "{}{}", rows)
