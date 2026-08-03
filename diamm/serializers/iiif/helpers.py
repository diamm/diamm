import re

from django.conf import settings
from django.template.loader import get_template
from django.utils.html import conditional_escape, format_html_join
from rest_framework.reverse import reverse

PRESENTATION_CONTEXT = "http://iiif.io/api/presentation/3/context.json"


def diamm_provider() -> list[dict]:
    homepage = f"https://{settings.HOSTNAME}/"
    return [
        {
            "id": homepage,
            "type": "Agent",
            "label": language_map(
                "Digital Image Archive of Medieval Music", "en"
            ),
            "homepage": [
                {
                    "id": homepage,
                    "type": "Text",
                    "format": "text/html",
                    "label": language_map(
                        "Digital Image Archive of Medieval Music", "en"
                    ),
                }
            ],
            "logo": [
                {
                    "id": f"{homepage}static/images/diammlogo.png",
                    "type": "Image",
                    "format": "image/png",
                }
            ],
        }
    ]


def process_composers_list(label: str, value: list, request) -> dict:
    composers = []
    for composer in value:
        name, pk, uncertain = composer.split("|")

        if uncertain and uncertain == "True":
            name = f"{name}?"

        name = conditional_escape(name)

        if pk:
            url = reverse("person-detail", kwargs={"pk": pk}, request=request)
            name = format_html_join("", '<a href="{}">{}</a>', ((url, name),))

        composers.append(name)

    composer_list = format_html_join("; ", "{}", ((name,) for name in composers))
    return {
        "label": language_map(label, "en"),
        "value": language_map(
            format_html_join("", "<span>{}</span>", ((composer_list,),))
        ),
    }


def process_voices_json(label: str, value: list, request) -> dict:
    del request
    template = get_template("website/iiif/item_voices.jinja2")
    block = template.template.render(content=value)
    # strip out any newlines from the templating process
    block = re.sub(r"\n", "", block)
    # strip out multiple spaces
    block = re.sub(r"\s+", " ", block)
    block = block.strip()
    return {"label": language_map(label, "en"), "value": language_map(block)}


def language_map(value: object, language: str = "none") -> dict[str, list[str]]:
    return {language: [str(value)]}


METADATA_MAPPING = [
    ("name_s", "Name", None),
    ("shelfmark_s", "Shelfmark", None),
    ("archive_s", "Archive", None),
    ("surface_type_s", "Surface Type", None),
    ("measurements_s", "Measurements", None),
    ("identifiers_ss", "Identifiers", None),
    ("date_statement_s", "Date Statement", None),
    ("source_type_s", "Source Type", None),
    ("composers_ssni", "Composers", process_composers_list),
    ("source_attribution_s", "Source Attribution", None),
    ("item_title_s", "Item Title", None),
    ("folio_start_s", "Start Folio / Page", None),
    ("folio_end_s", "End Folio / Page", None),
    ("genres_ss", "Genres", None),
    ("voices_json", "Voices", process_voices_json),
]


def create_metadata_block(obj: dict, request) -> list[dict]:
    metadata_entries = []
    for field, label, processor in METADATA_MAPPING:
        if field not in obj:
            continue

        field_value = obj[field]
        if processor is not None:
            metadata_entries.append(processor(label, field_value, request))
        elif isinstance(field_value, list):
            metadata_entries.append(
                {
                    "label": language_map(label, "en"),
                    "value": language_map("; ".join(field_value)),
                }
            )
        else:
            metadata_entries.append(
                {"label": language_map(label, "en"), "value": language_map(field_value)}
            )
    return metadata_entries
