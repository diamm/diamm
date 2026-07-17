from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from django.db.models import Model, UniqueConstraint


class MergeConflictError(RuntimeError):
    """Raised when merging would discard or overwrite related data."""


@dataclass(frozen=True)
class UniqueRule:
    fields: tuple[str, ...]
    nulls_distinct: bool | None = True


def _generic_foreign_keys() -> Iterator[GenericForeignKey]:
    for model in apps.get_models():
        for field in model._meta.private_fields:
            if isinstance(field, GenericForeignKey):
                yield field


def _unique_rules(model: type[Model]) -> list[UniqueRule]:
    rules = [
        UniqueRule((field.name,))
        for field in model._meta.concrete_fields
        if field.unique and not field.primary_key
    ]
    rules.extend(UniqueRule(tuple(fields)) for fields in model._meta.unique_together)
    rules.extend(
        UniqueRule(tuple(constraint.fields), constraint.nulls_distinct)
        for constraint in model._meta.constraints
        if isinstance(constraint, UniqueConstraint)
        and constraint.fields
        and constraint.condition is None
        and not constraint.expressions
    )
    return rules


def _matching_unique_object(
    instance: Model, relation_field_name: str
) -> Model | None:
    model = type(instance)
    for rule in _unique_rules(model):
        if relation_field_name not in rule.fields:
            continue

        values = {
            model._meta.get_field(name).attname: getattr(
                instance, model._meta.get_field(name).attname
            )
            for name in rule.fields
        }
        if rule.nulls_distinct is not False and any(
            value is None for value in values.values()
        ):
            continue

        match = model._default_manager.exclude(pk=instance.pk).filter(**values).first()
        if match is not None:
            return match
    return None


def _equivalent_except_relation(
    first: Model, second: Model, relation_field_name: str
) -> bool:
    for field in first._meta.concrete_fields:
        if field.primary_key or field.name == relation_field_name:
            continue
        if getattr(first, field.attname) != getattr(second, field.attname):
            return False
    return True


def _has_related_data(instance: Model) -> bool:
    for relation in instance._meta.related_objects:
        accessor = relation.get_accessor_name()
        if not accessor:
            continue
        try:
            related = getattr(instance, accessor)
        except ObjectDoesNotExist:
            continue
        if relation.one_to_one:
            return True
        if related.exists():
            return True

    for field in instance._meta.many_to_many:
        if getattr(instance, field.name).exists():
            return True

    content_type = ContentType.objects.get_for_model(instance)
    for field in _generic_foreign_keys():
        if field.model._default_manager.filter(
            **{
                field.ct_field: content_type,
                field.fk_field: instance.pk,
            }
        ).exists():
            return True
    return False


def _move_related_object(
    related: Model, relation_field_name: str, primary: Model
) -> None:
    setattr(related, relation_field_name, primary)
    duplicate = _matching_unique_object(related, relation_field_name)
    if duplicate is not None:
        if _equivalent_except_relation(related, duplicate, relation_field_name) and not (
            _has_related_data(related)
        ):
            related.delete()
            return
        raise MergeConflictError(
            f"Cannot merge {type(primary)._meta.verbose_name} records: "
            f"moving {related._meta.verbose_name} {related.pk} would conflict "
            f"with {duplicate.pk}. Resolve these related records first."
        )

    try:
        with transaction.atomic():
            related.save(update_fields=(relation_field_name,))
    except IntegrityError as exc:
        raise MergeConflictError(
            f"Cannot merge {type(primary)._meta.verbose_name} records because "
            f"{related._meta.verbose_name} {related.pk} violates a database constraint."
        ) from exc


def _move_reverse_relations(primary: Model, alias: Model) -> None:
    for relation in primary._meta.related_objects:
        accessor = relation.get_accessor_name()
        if not accessor:
            continue

        if relation.many_to_many:
            through = relation.field.remote_field.through
            if not through._meta.auto_created:
                continue
            alias_manager = getattr(alias, accessor)
            primary_manager = getattr(primary, accessor)
            related = list(alias_manager.all())
            primary_manager.add(*related)
            alias_manager.clear()
            continue

        relation_field_name = relation.field.name
        if relation.one_to_one:
            try:
                related_objects = [getattr(alias, accessor)]
            except ObjectDoesNotExist:
                related_objects = []
        else:
            related_objects = list(
                getattr(alias, accessor).select_for_update().all()
            )

        for related in related_objects:
            _move_related_object(related, relation_field_name, primary)


def _merge_local_many_to_many(primary: Model, alias: Model) -> None:
    for field in primary._meta.many_to_many:
        through = field.remote_field.through
        if not through._meta.auto_created:
            continue
        alias_manager = getattr(alias, field.name)
        primary_manager = getattr(primary, field.name)
        related = list(alias_manager.all())
        primary_manager.add(*related)
        alias_manager.clear()


def _move_generic_relations(primary: Model, alias: Model) -> None:
    alias_content_type = ContentType.objects.get_for_model(alias)
    primary_content_type = ContentType.objects.get_for_model(primary)
    for field in _generic_foreign_keys():
        related_objects = field.model._default_manager.select_for_update().filter(
            **{
                field.ct_field: alias_content_type,
                field.fk_field: alias.pk,
            }
        )
        for related in related_objects:
            setattr(related, field.ct_field, primary_content_type)
            setattr(related, field.fk_field, primary.pk)
            related.save(update_fields=(field.ct_field, field.fk_field))


def _fill_blank_primary_fields(primary: Model, aliases: Iterable[Model]) -> None:
    blank_fields = {
        field.attname
        for field in primary._meta.concrete_fields
        if field.editable
        and not field.primary_key
        and getattr(primary, field.attname) in (None, "")
    }
    for alias in aliases:
        filled = set()
        for field_name in blank_fields:
            value = getattr(alias, field_name)
            if value not in (None, ""):
                setattr(primary, field_name, value)
                filled.add(field_name)
        blank_fields -= filled


@transaction.atomic
def merge(
    primary_object: Model,
    alias_objects: Model | Iterable[Model] | None,
    keep_old: bool = False,
) -> Model:
    """Merge aliases into a primary object without silently losing related data.

    The primary record wins for populated scalar fields. Blank primary fields are
    filled from aliases in the supplied order. Reverse foreign keys, generic
    foreign keys, and automatic many-to-many memberships move to the primary.
    Exact duplicate rows created by an unconditional uniqueness rule are collapsed
    only when they have no dependent data; differing duplicates raise
    ``MergeConflictError`` and roll back the complete merge.
    """

    if not isinstance(primary_object, Model):
        raise TypeError("Only Django model instances can be merged")
    if primary_object.pk is None:
        raise ValueError("The primary object must be saved before it can be merged")

    if alias_objects is None:
        aliases: list[Model] = []
    elif isinstance(alias_objects, Model):
        aliases = [alias_objects]
    else:
        aliases = list(alias_objects)

    primary_class = type(primary_object)
    if any(type(alias) is not primary_class for alias in aliases):
        raise TypeError("Only instances of the same model can be merged")
    if any(alias.pk is None for alias in aliases):
        raise ValueError("Every alias object must be saved before it can be merged")
    if primary_object.pk in {alias.pk for alias in aliases}:
        raise ValueError("The primary object cannot also be an alias")
    if len({alias.pk for alias in aliases}) != len(aliases):
        raise ValueError("An alias object cannot be merged more than once")

    primary = primary_class._default_manager.select_for_update().get(
        pk=primary_object.pk
    )
    locked_aliases_by_pk = {
        alias.pk: alias
        for alias in primary_class._default_manager.select_for_update().filter(
            pk__in=[alias.pk for alias in aliases]
        )
    }
    if len(locked_aliases_by_pk) != len(aliases):
        raise ValueError("One or more alias objects no longer exist")
    locked_aliases = [locked_aliases_by_pk[alias.pk] for alias in aliases]

    _fill_blank_primary_fields(primary, locked_aliases)
    primary.save()

    for alias in locked_aliases:
        _move_reverse_relations(primary, alias)
        _merge_local_many_to_many(primary, alias)
        _move_generic_relations(primary, alias)
        if not keep_old:
            alias.delete()

    return primary
