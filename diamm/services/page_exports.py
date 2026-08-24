from dataclasses import dataclass
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max

from diamm.models import Image, Page, Source


@dataclass(frozen=True)
class PageExportResult:
    pages: tuple[Page, ...]
    images: tuple[Image, ...]


def _concrete_values(instance, *, exclude=()):
    excluded = set(exclude)
    return {
        field.attname: getattr(instance, field.attname)
        for field in instance._meta.concrete_fields
        if field.name not in excluded and field.attname not in excluded
    }


@transaction.atomic
def export_pages_to_source(*, source, target, pages) -> PageExportResult:
    """Copy selected pages and their images from one source to another."""
    source = Source.objects.get(pk=source.pk)
    target = Source.objects.select_for_update().get(pk=target.pk)
    selected_ids = [page.pk for page in pages]

    errors = []
    if source.pk == target.pk:
        errors.append("Choose a different target source.")
    if not selected_ids:
        errors.append("Select at least one page to export.")
    if len(selected_ids) != len(set(selected_ids)):
        errors.append("A page may only be selected once.")

    selected = list(
        Page.objects.filter(pk__in=selected_ids, source=source)
        .prefetch_related("images")
        .order_by("sort_order", "pk")
    )
    if len(selected) != len(selected_ids):
        errors.append("Every selected page must belong to this source.")
    if errors:
        raise ValidationError(errors)

    next_page_order = (
        target.pages.aggregate(value=Max("sort_order"))["value"] or Decimal(-1)
    ) + Decimal(1)
    new_pages = []
    new_images = []
    for offset, original in enumerate(selected):
        page = Page.objects.create(
            source=target,
            sort_order=next_page_order + offset,
            **_concrete_values(
                original,
                exclude={"id", "source", "copied_from", "sort_order"},
            ),
        )
        new_pages.append(page)

        for original_image in original.images.all():
            image = Image.objects.create(
                page=page,
                **_concrete_values(
                    original_image,
                    exclude={"id", "page", "created", "updated"},
                ),
            )
            new_images.append(image)

    return PageExportResult(pages=tuple(new_pages), images=tuple(new_images))
