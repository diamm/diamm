from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token


class DiammToken(Token):
    """
    The default authorization token model.
    """

    class Meta:
        app_label = "diamm_site"
        verbose_name = "DIAMM Token"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="auth_tokens",
        on_delete=models.CASCADE,
        verbose_name=_("User"),
    )
    domain = models.CharField(_("Domain"), max_length=128)
    created = models.DateTimeField(_("Created"), auto_now_add=True)
