from django import forms
from django.contrib import admin
from django.contrib.auth import password_validation
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import gettext_lazy as _

from diamm.models.diamm_user import CustomUserModel


class UserCreationForm(forms.ModelForm):
    """
    A replication of the User Creation Form for users with passwords.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self._meta.model.USERNAME_FIELD].widget.attrs.update(
            {"autofocus": ""}
        )

    class Meta:
        model = CustomUserModel
        fields = ("email",)

    error_messages = {"password_mismatch": _("The two password fields didn't match")}

    password1 = forms.CharField(
        label=_("Password"), strip=False, widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        strip=False,
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as before, for verification"),
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages["password_mismatch"], code="password_mismatch"
            )
        password_validation.validate_password(
            self.cleaned_data.get("password2", ""), self.instance
        )
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    An implementation of the user change form.
    Essentially replicates django.contrib.auth.forms.UserChangeForm
    """

    class Meta:
        model = CustomUserModel
        fields = "__all__"  # noqa: DJ007

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        f = self.fields.get("user_permissions")
        if f is not None:
            f.queryset = f.queryset.select_related("content_type")

    password = ReadOnlyPasswordHashField(
        label=_("Password"),
        help_text=_(
            "Raw passwords are not stored, so there is no way to see this "
            "user's password, but you can change the password using "
            '<a href="../password/">this form</a>.'
        ),
    )

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class CommentaryFilter(admin.SimpleListFilter):
    title = _("Commentary")
    parameter_name = "commentary"

    def lookups(self, request, model_admin):
        return (
            ("yes", _("User has commentary")),
            ("no", _("User does not have commentary")),
        )

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        val = self.value()
        if val == "yes":
            return queryset.filter(commentaries__isnull=False).distinct()
        elif val == "no":
            return queryset.filter(commentaries__isnull=True).distinct()


@admin.register(CustomUserModel)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_per_page = 400
    list_display = (
        "email",
        "affiliation",
        "is_active",
        "is_staff",
        "legacy_username",
        "last_login",
    )
    list_filter = (
        "is_staff",
        "is_active",
        "is_superuser",
        CommentaryFilter,
        ("last_login", admin.EmptyFieldListFilter),
    )

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "affiliation")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (_("Administration"), {"fields": ("legacy_id",)}),
    )

    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
    )

    search_fields = ("email", "affiliation", "last_name", "first_name")
    ordering = ("date_joined",)
