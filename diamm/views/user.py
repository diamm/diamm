from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework import views
from rest_framework import renderers
from rest_framework.response import Response
from diamm.renderers.html_renderer import HTMLRenderer
from diamm.serializers.website.user import UserSerializer
from diamm.forms.account_edit_form import AccountEditForm


@method_decorator(login_required, name='dispatch')
class ProfileView(views.APIView):
    template_name = "website/user/profile.jinja2"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)

    def get(self, request, *args, **kwargs):
        user = request.user
        data = UserSerializer(user, context={"request": request}).data
        return Response(data)


@method_decorator(login_required(login_url="/login/"), name='dispatch')
class ProfileEditView(FormView):
    form_class = AccountEditForm
    template_name = "website/user/profile-edit.jinja2"
    success_url = "/account/"

    def form_valid(self, form):
        response = super(ProfileEditView, self).form_valid(form)
        user = self.request.user

        user.email = form.cleaned_data.get('email')
        user.affiliation = form.cleaned_data.get('affiliation')
        user.first_name = form.cleaned_data.get('first_name')
        user.last_name = form.cleaned_data.get('last_name')
        user.save()

        return response

    def get_initial(self):
        user = self.request.user
        initial_data = {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'affiliation': user.affiliation
        }
        return initial_data
