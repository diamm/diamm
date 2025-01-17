from collections.abc import Iterable

from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import transaction
from django.db.models import Model


def flatten(flist, a: list):
    """Flattens a list.  Just do flatten(l, [])."""
    for i in flist:
        if isinstance(i, Iterable) and not isinstance(i, str):
            flatten(i, a)
        else:
            a.append(i)
    return a


def is_duplicate_in_model(instance):
    """
    Check if the unique field values in instance already exist elsewhere in the model.
    Typically checked prior to saving the instance.
    :param instance: The instance to check for duplicates of in the instance model.
    :return: True if the instance is found in the model, and it is not itself.
    """
    fields = flatten(instance._meta.unique_together, [])
    if fields:
        return (
            type(instance)
            .objects.exclude(pk=instance.pk)
            .filter(**{k: getattr(instance, k) for k in fields})
            .count()
            > 0
        )

    return False


@transaction.atomic()
def merge(primary_object, alias_objects, keep_old=False):
    """
    Use this function to merge model objects (i.e. Users, Organizations, Polls,
    etc.) and migrate all of the related fields from the alias objects to the
    primary object.

    Usage:
    from django.contrib.auth.models import User
    primary_user = User.objects.get(email='good_email@example.com')
    duplicate_user = User.objects.get(email='good_email+duplicate@example.com')
    merge_model_objects(primary_user, duplicate_user)
    """
    if alias_objects is None:
        alias_objects = []

    if not isinstance(alias_objects, list):
        alias_objects = [alias_objects]

    # check that all aliases are the same class as primary one and that
    # they are subclass of model
    primary_class = primary_object.__class__

    if not issubclass(primary_class, Model):
        raise TypeError("Only django.db.models.Model subclasses can be merged")

    for alias_object in alias_objects:
        if not isinstance(alias_object, primary_class):
            raise TypeError("Only models of same class can be merged")

    # Get a list of all GenericForeignKeys in all models
    # TODO: this is a bit of a hack, since the generics framework should provide a similar
    # method to the ForeignKey field for accessing the generic related fields.
    generic_fields = []
    # Only get the models for the 'diamm_data' app.
    for model in apps.get_app_config("diamm_data").get_models():
        for _, field in filter(
            lambda x: isinstance(x[1], GenericForeignKey), model.__dict__.items()
        ):
            generic_fields.append(field)

    blank_local_fields = {
        field.attname
        for field in primary_object._meta.local_fields
        if getattr(primary_object, field.attname) in [None, ""]
    }

    # Loop through all alias objects and migrate their data to the primary object.
    for alias_object in alias_objects:
        # Migrate all foreign key references from alias object to primary object.
        for related_object in alias_object._meta.related_objects:
            # The variable name on the alias_object model.
            related_name = related_object.get_accessor_name()

            if related_object.field.many_to_one:
                for obj in getattr(alias_object, related_name).all().all():
                    setattr(obj, related_object.field.name, primary_object)
                    if not is_duplicate_in_model(obj):
                        obj.save()

            elif related_object.field.one_to_one:
                setattr(alias_object, related_object.field.name, primary_object)
                alias_object.save()

            elif related_object.field.many_to_many:
                related_name = related_name or related_object.field.name
                for obj in getattr(alias_object, related_name).all():
                    getattr(obj, related_name).remove(alias_object)
                    getattr(obj, related_name).add(primary_object)

        # Migrate all generic foreign key references from alias object to primary object.
        for field in generic_fields:
            filter_kwargs: dict = {
                field.fk_field: alias_object._get_pk_val(),
                field.ct_field: field.get_content_type(alias_object),
            }
            for generic_related_object in field.model.objects.filter(**filter_kwargs):
                setattr(generic_related_object, field.name, primary_object)
                generic_related_object.save()

        # Try to fill all missing values in primary object by values of duplicates
        filled_up = set()
        for field_name in blank_local_fields:
            val = getattr(alias_object, field_name)
            if val not in [None, ""]:
                setattr(primary_object, field_name, val)
                filled_up.add(field_name)
        blank_local_fields -= filled_up

        if not keep_old:
            alias_object.delete()

    primary_object.save()

    return primary_object
