from django.contrib.admin import widgets
from django.contrib.admin.options import get_ul_class
from django.contrib.admin.widgets import AutocompleteSelect
from django.forms import boundfield, models
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _


class ForeignKeyRawIdWidget(widgets.ForeignKeyRawIdWidget):
    def format_value(self, value):
        """Try to return the `pk` if value is an object, otherwise just return
        the value as fallback."""

        if value == "" or value is None:
            return None

        try:
            return str(value.pk)
        except AttributeError:
            return str(value)

    def label_and_url_for_value(self, value):
        """Instead of the original we do not have do a `get()` anymore instead
        access the instance directly so when value is prefetched this will
        prevent additional queries."""

        try:
            pk = value.pk
            meta = value._meta
        except AttributeError:
            # Fallback for compatibility with plain pk values
            return super().label_and_url_for_value(value)

        try:
            url = reverse(
                f"{self.admin_site.name}:{meta.app_label}_{meta.object_name.lower()}_change",
                args=(pk,),
            )
        except NoReverseMatch:
            url = ""  # Admin not registered for target model.

        return Truncator(value).words(14), url


class BoundField(boundfield.BoundField):
    def value(self):
        """Return the instance instead of plain value if possible.
        In order for `ForeignKeyRawIdWidget` to access the model instance directly
        we grab if from the form if available."""

        if type(self.field.widget) == ForeignKeyRawIdWidget:
            try:
                return getattr(self.form.instance, self.name)
            except AttributeError:
                pass

        # Otherwise default behaviour
        return super().value()


class ModelChoiceField(models.ModelChoiceField):
    def get_bound_field(self, form, field_name):
        """Return our custom `BoundField`."""

        return BoundField(form, self, field_name)


class RawIdWidgetAdminMixin:
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """ModelAdmin mixin that uses a custom `ForeignKeyRawIdWidget`.
        This prevents extra queries when the queryset has been prefetched using
        `prefetch_related()`. Only works when `raw_id_fields` is filled."""

        if db_field.name not in self.raw_id_fields:
            # If we are not using raw_id_fields then skip the whole thing
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

        db = kwargs.get("using")

        if "widget" not in kwargs:
            if db_field.name in self.get_autocomplete_fields(request):
                kwargs["widget"] = AutocompleteSelect(
                    db_field.remote_field, self.admin_site, using=db
                )
            elif db_field.name in self.raw_id_fields:
                # Using our modified ForeignKeyRawIdWidget here instead
                kwargs["widget"] = ForeignKeyRawIdWidget(
                    db_field.remote_field, self.admin_site, using=db
                )
            elif db_field.name in self.radio_fields:
                kwargs["widget"] = widgets.AdminRadioSelect(
                    attrs={
                        "class": get_ul_class(self.radio_fields[db_field.name]),
                    }
                )
                kwargs["empty_label"] = _("None") if db_field.blank else None

        if "queryset" not in kwargs:
            queryset = self.get_field_queryset(db, db_field, request)
            if queryset is not None:
                kwargs["queryset"] = queryset

        if isinstance(db_field.remote_field.model, str):
            raise ValueError(
                f"Cannot create form field for {db_field.name!r} yet, because "
                "its related model {db_field.remote_field.model!r} has not been loaded yet"
            )
        return super(type(db_field), db_field).formfield(
            **{
                # Using our modified ModelChoiceField here instead
                "form_class": ModelChoiceField,
                "queryset": db_field.remote_field.model._default_manager.using(db),
                "to_field_name": db_field.remote_field.field_name,
                **kwargs,
                "blank": db_field.blank,
            }
        )
