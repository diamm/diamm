from dataclasses import dataclass
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max

from diamm.models import (
    Image,
    ImageNote,
    Item,
    ItemBibliography,
    ItemComposer,
    ItemNote,
    Page,
    PageNote,
    Source,
    SourceToSourceRelationship,
    Voice,
)


@dataclass(frozen=True)
class VirtualSourceImportResult:
    pages: tuple[Page, ...]
    items: tuple[Item, ...]
    images: tuple[Image, ...]
    relationship_created: bool


def _concrete_values(instance, *, exclude=()):
    excluded = set(exclude)
    return {
        field.attname: getattr(instance, field.attname)
        for field in instance._meta.concrete_fields
        if field.name not in excluded and field.attname not in excluded
    }


@transaction.atomic
def copy_pages_to_virtual_source(
    *, target, donor, pages, relationship_type=None
) -> VirtualSourceImportResult:
    """Copy selected internal donor pages and their inventory into a virtual source."""
    target = Source.objects.select_for_update().get(pk=target.pk)
    donor = Source.objects.get(pk=donor.pk)
    selected = list(pages)

    errors = []
    if not target.is_virtual:
        errors.append("The target source is not virtual.")
    if donor.is_virtual:
        errors.append("A virtual source cannot be used as a donor.")
    if not selected:
        errors.append("Select at least one page to copy.")
    if any(page.source_id != donor.pk for page in selected):
        errors.append("Every selected page must belong to the donor source.")
    if any(page.external for page in selected):
        errors.append("External pages cannot be copied into a virtual source.")
    selected_ids = [page.pk for page in selected]
    if len(selected_ids) != len(set(selected_ids)):
        errors.append("A page may only be selected once.")
    if Page.objects.filter(source=target, copied_from_id__in=selected_ids).exists():
        errors.append("One or more selected pages have already been copied.")
    if errors:
        raise ValidationError(errors)

    selected.sort(
        key=lambda page: (
            page.sort_order is None,
            page.sort_order if page.sort_order is not None else Decimal(0),
            page.pk,
        )
    )
    next_page_order = (
        target.pages.aggregate(value=Max("sort_order"))["value"] or Decimal(-1)
    ) + Decimal(1)

    page_map = {}
    new_pages = []
    new_images = []
    for offset, original in enumerate(selected):
        clone = Page.objects.create(
            **_concrete_values(
                original,
                exclude={
                    "id",
                    "source",
                    "copied_from",
                    "sort_order",
                    "legacy_id",
                    "iiif_canvas_uri",
                    "external",
                },
            ),
            source=target,
            copied_from=original,
            sort_order=next_page_order + offset,
            legacy_id=None,
            iiif_canvas_uri=None,
            external=False,
        )
        page_map[original.pk] = clone
        new_pages.append(clone)

        PageNote.objects.bulk_create(
            [
                PageNote(
                    page=clone,
                    **_concrete_values(note, exclude={"id", "page"}),
                )
                for note in original.notes.all()
            ]
        )
        for original_image in original.images.all():
            image = Image.objects.create(
                page=clone,
                **_concrete_values(
                    original_image,
                    exclude={"id", "page", "legacy_id", "created", "updated"},
                ),
                legacy_id=None,
            )
            new_images.append(image)
            ImageNote.objects.bulk_create(
                [
                    ImageNote(
                        image=image,
                        **_concrete_values(note, exclude={"id", "image"}),
                    )
                    for note in original_image.imagenote_set.all()
                ]
            )

    originals = list(
        Item.objects.filter(source=donor, pages__pk__in=selected_ids)
        .distinct()
        .prefetch_related(
            "pages",
            "voices__languages",
            "notes",
            "itembibliography_set",
            "unattributed_composers",
        )
    )
    page_position = {page.pk: position for position, page in enumerate(selected)}
    originals.sort(
        key=lambda item: (
            min(page_position[p.pk] for p in item.pages.all() if p.pk in page_position),
            item.source_order is None,
            item.source_order if item.source_order is not None else Decimal(0),
            item.pk,
        )
    )
    next_item_order = (
        target.inventory.aggregate(value=Max("source_order"))["value"] or Decimal(-1)
    ) + Decimal(1)
    new_items = []
    for original in originals:
        clone = Item.objects.filter(source=target, copied_from=original).first()
        if clone is None:
            clone = Item.objects.create(
                source=target,
                copied_from=original,
                source_order=next_item_order + len(new_items),
                **_concrete_values(
                    original,
                    exclude={
                        "id",
                        "source",
                        "copied_from",
                        "source_order",
                        "created",
                        "updated",
                    },
                ),
            )
            new_items.append(clone)
            for original_voice in original.voices.all():
                voice = Voice.objects.create(
                    item=clone,
                    **_concrete_values(original_voice, exclude={"id", "item"}),
                )
                voice.languages.set(original_voice.languages.all())
            ItemNote.objects.bulk_create(
                [
                    ItemNote(
                        item=clone,
                        **_concrete_values(note, exclude={"id", "item"}),
                    )
                    for note in original.notes.all()
                ]
            )
            ItemBibliography.objects.bulk_create(
                [
                    ItemBibliography(
                        item=clone,
                        **_concrete_values(entry, exclude={"id", "item"}),
                    )
                    for entry in original.itembibliography_set.all()
                ]
            )
            ItemComposer.objects.bulk_create(
                [
                    ItemComposer(
                        item=clone,
                        **_concrete_values(composer, exclude={"id", "item"}),
                    )
                    for composer in original.unattributed_composers.all()
                ]
            )

        clone.pages.add(
            *(page_map[page.pk] for page in original.pages.all() if page.pk in page_map)
        )

    relationship_created = False
    if relationship_type is not None:
        _, relationship_created = SourceToSourceRelationship.objects.get_or_create(
            from_source=target,
            to_source=donor,
            relationship_type=relationship_type,
        )

    updates = {}
    if target.public_images and not donor.public_images:
        updates["public_images"] = False
    if target.open_images and not donor.open_images:
        updates["open_images"] = False
    if updates:
        Source.objects.filter(pk=target.pk).update(**updates)

    return VirtualSourceImportResult(
        pages=tuple(new_pages),
        items=tuple(new_items),
        images=tuple(new_images),
        relationship_created=relationship_created,
    )
