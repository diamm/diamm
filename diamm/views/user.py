from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView
from rest_framework import views
from rest_framework.response import Response

from diamm.forms.account_edit_form import AccountEditForm
from diamm.renderers.html_renderer import HTMLRenderer
from diamm.renderers.ujson_renderer import UJSONRenderer
from diamm.serializers.website.user import UserSerializer


@method_decorator(login_required, name="dispatch")
class ProfileView(views.APIView):
    template_name = "website/user/profile.jinja2"
    renderer_classes = (HTMLRenderer, UJSONRenderer)

    def get(self, request, *args, **kwargs) -> Response:
        user = request.user
        data = UserSerializer(user, context={"request": request}).data
        return Response(data)


@method_decorator(login_required(login_url="/login/"), name="dispatch")
class ProfileEditView(FormView):
    form_class = AccountEditForm
    template_name = "website/user/profile-edit.jinja2"
    success_url = "/account/"

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.request.user

        user.email = form.cleaned_data.get("email")
        user.affiliation = form.cleaned_data.get("affiliation")
        user.first_name = form.cleaned_data.get("first_name")
        user.last_name = form.cleaned_data.get("last_name")
        user.save()

        return response

    def get_initial(self) -> dict:
        user = self.request.user
        if user.is_anonymous:
            return {}

        initial_data = {
            "email": user.email,  # type: ignore
            "first_name": user.first_name,  # type: ignore
            "last_name": user.last_name,  # type: ignore
            "affiliation": user.affiliation,  # type: ignore
        }
        return initial_data
