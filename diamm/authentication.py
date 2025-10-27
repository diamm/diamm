from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication, get_authorization_header

from diamm.auth_local import check_auth
from diamm.models import CustomUserModel
from diamm.models.diamm_token import DiammToken


class DiammTokenAuthentication(TokenAuthentication):
    model = DiammToken

    def authenticate(self, request) -> tuple[CustomUserModel, str] | None:
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _("Invalid token header. No credentials provided.")
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _("Invalid token header. Token string should not contain spaces.")
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError as err:
            msg = _(
                "Invalid token header. Token string should not contain invalid characters."
            )
            raise exceptions.AuthenticationFailed(msg) from err

        domain: str | None = request.META.get("HTTP_X_DIAMM_ORIGIN")
        if not domain:
            msg = _("A DIAMM Domain header is required for token authentication.")
            raise exceptions.AuthenticationFailed(msg)

        secret: str | None = request.META.get("HTTP_X_DIAMM_SECRET")
        if not secret:
            msg = _("A DIAMM Secret header is required for token authentication.")
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_enhanced_credentials(token, domain, secret)

    def authenticate_enhanced_credentials(
        self, key: str, domain: str, secret: str
    ) -> tuple[CustomUserModel, str]:
        model = self.get_model()
        try:
            token = model.objects.select_related("user").get(key=key)
        except model.DoesNotExist as err:
            raise exceptions.AuthenticationFailed(_("Invalid token.")) from err

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_("User inactive or deleted."))

        if domain not in token.domain:
            raise exceptions.AuthenticationFailed(_("Invalid origin domain."))

        check_secret = check_auth(key, secret)
        if not check_secret:
            raise exceptions.AuthenticationFailed(_("Invalid secret value."))

        return token.user, token

    def authenticate_header(self, request):
        return self.keyword
