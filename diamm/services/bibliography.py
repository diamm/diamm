from collections import defaultdict

from django.db import transaction

from diamm.admin.merge_models import MergeConflictError, merge
from diamm.models import (
    BibliographyAuthorRole,
    BibliographyPublication,
    CompositionBibliography,
    ItemBibliography,
    SetBibliography,
    SourceBibliography,
)


def _collapse_exact_duplicates(queryset, field_names):
    seen = set()
    duplicate_ids = []
    for row in queryset.order_by("pk"):
        signature = tuple(getattr(row, field_name) for field_name in field_names)
        if signature in seen:
            duplicate_ids.append(row.pk)
        else:
            seen.add(signature)
    if duplicate_ids:
        queryset.model.objects.filter(pk__in=duplicate_ids).delete()


def _deduplicate_attachments(*, bibliography, model, related_field, metadata_fields):
    grouped = defaultdict(list)
    queryset = model.objects.filter(bibliography=bibliography)
    for row in queryset.order_by("pk"):
        grouped[getattr(row, f"{related_field}_id")].append(row)

    duplicate_ids = []
    for related_id, rows in grouped.items():
        signatures = {
            tuple(getattr(row, field_name) for field_name in metadata_fields)
            for row in rows
        }
        if len(signatures) > 1:
            record_ids = ", ".join(str(row.pk) for row in rows)
            raise MergeConflictError(
                f"Cannot merge bibliography entries: {model._meta.verbose_name_plural} "
                f"{record_ids} attach to the same {related_field} {related_id} with "
                "different metadata. Resolve these records first."
            )
        duplicate_ids.extend(row.pk for row in rows[1:])

    if duplicate_ids:
        model.objects.filter(pk__in=duplicate_ids).delete()


@transaction.atomic
def merge_bibliographies(primary, aliases, *, keep_old=False):
    """Merge bibliography records without duplicating citations or child metadata."""
    merged = merge(primary, aliases, keep_old=keep_old)

    _collapse_exact_duplicates(
        BibliographyAuthorRole.objects.filter(bibliography_entry=merged),
        ("bibliography_author_id", "role", "position"),
    )
    _collapse_exact_duplicates(
        BibliographyPublication.objects.filter(bibliography=merged),
        ("type", "entry"),
    )

    for model, related_field, metadata_fields in (
        (
            SourceBibliography,
            "source",
            ("primary_study", "pages", "notes"),
        ),
        (ItemBibliography, "item", ("pages", "notes")),
        (
            CompositionBibliography,
            "composition",
            ("pages", "notes"),
        ),
        (SetBibliography, "set", ("pages", "notes")),
    ):
        _deduplicate_attachments(
            bibliography=merged,
            model=model,
            related_field=related_field,
            metadata_fields=metadata_fields,
        )

    return merged
