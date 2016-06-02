from rest_framework import views, renderers, permissions
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from diamm.renderers.html_renderer import HTMLRenderer
from diamm.forms.contribution_form import ContributionForm


class MakeContribution(views.APIView):
    template_name = "website/contribution/contribution.jinja2"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        form = ContributionForm(request.POST)
        object_id = request.data.get('pk')
        content_type = request.data.get('type')
        current_url = request.GET.get('from', None)

        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.note = request.data.get('note')
            contribution.object_id = object_id
            contribution.contributor = request.user

            try:
                contribution.content_type = ContentType.objects.get(app_label="diamm_data", model=content_type)
            except ObjectDoesNotExist:
                messages.success(request._request, 'Invalid content type')
                return HttpResponseRedirect(current_url)

            try:
                contribution.content_type.model_class().objects.all().get(pk=contribution.object_id)
            except ObjectDoesNotExist:
                messages.success(request._request, 'Invalid Object')
                return HttpResponseRedirect(current_url)

            if not request.user.is_authenticated():
                messages.success(request._request, 'Invalid User')
                return HttpResponseRedirect(current_url)

            contribution.save()
            messages.success(request._request, 'Your contribution was submitted')
            return HttpResponseRedirect(current_url)

        if not request.data.get('note'):
            messages.success(request._request, 'You did not enter a contribution')
        return HttpResponseRedirect(current_url)

