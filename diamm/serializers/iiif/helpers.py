import re

from django.template.loader import get_template


def process_composers_list(label: str, value: list) -> dict:
    composers = []
    for composer in value:
        name, pk, uncertain = composer.split("|")

        if uncertain and uncertain == "True":
            name = f"{name}?"

        composers.append(name)
    return {"label": label, "value": "; ".join(composers)}


def process_voices_json(label: str, value: list) -> dict:
    template = get_template("website/iiif/item_voices.jinja2")
    block = template.template.render(content=value)
    # strip out any newlines from the templating process
    block = re.sub(r"\n", "", block)
    # strip out multiple spaces
    block = re.sub(r"\s+", " ", block)
    block = block.strip()
    return {"label": label, "value": block}


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


def create_metadata_block(obj: dict) -> list[dict]:
    metadata_entries = []
    for field, label, processor in METADATA_MAPPING:
        if field not in obj:
            continue

        field_value = obj[field]
        if processor is not None:
            metadata_entries.append(processor(label, field_value))
        elif isinstance(field_value, list):
            metadata_entries.append({"label": label, "value": "; ".join(field_value)})
        else:
            metadata_entries.append({"label": label, "value": field_value})
    return metadata_entries
