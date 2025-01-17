from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    A copy of django.contrib.auth.models.UserManager, but which does not need a username. Instead, an e-mail
    address is used for the username.
    """

    use_in_migration = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("You must provide an e-mail address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class CustomUserModel(AbstractBaseUser, PermissionsMixin):
    """
    A custom user model for DIAMM that uses an e-mail address as the username.
    Essentially a copy of django.contrib.auth.models.AbstractUser.
    """

    class Meta:
        app_label = "diamm_site"
        verbose_name = "User"

    email = models.EmailField(_("email address"), max_length=255, unique=True)
    first_name = models.CharField(_("first name"), max_length=30, blank=True, null=True)
    last_name = models.CharField(_("last name"), max_length=30, blank=True, null=True)
    affiliation = models.CharField(
        _("affiliation"), max_length=255, blank=True, null=True
    )
    legacy_username = models.CharField(
        _("legacy username"), max_length=255, blank=True, null=True
    )
    legacy_id = models.IntegerField(_("legacy id"), blank=True, null=True)

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )

    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"

    @property
    def full_name(self) -> str:
        return self.get_full_name()

    def get_full_name(self) -> str:
        if not self.last_name:
            return f"{self.email}"

        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self) -> str:
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs) -> str:
        send_mail(subject, message, from_email, [self.email], **kwargs)
