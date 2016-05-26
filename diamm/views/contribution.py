from rest_framework import views
from diamm.renderers.html_renderer import HTMLRenderer
from django.shortcuts import render
from rest_framework import renderers
from django.http import HttpResponseRedirect
from rest_framework.response import Response
from diamm.forms.contribution_form import ContributionForm
from diamm.models.site.contribution import Contribution
from diamm.serializers.website.contribution import ContributionSerializer


class MakeContribution(views.APIView):
    template_name = "contribution.jinja2"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)

    def post(self, request, *args, **kwargs):
        if request.method == "POST":
            form = ContributionForm(request.POST)

            if form.is_valid():
                contribution = form.save(commit=False)
                contribution.contributor = request.user
                contribution.save()
                return HttpResponseRedirect('contribution-submitted')
        else:
            form = ContributionForm()
        return render(request, 'website/contribution/contribution_submitted.jinja2', {'form': form})

    def get(self, request, *args, **kwargs):
        form = ContributionForm(request.POST)
        if form.is_valid():
            contribution = form.save(commit=False)
            contribution.note = request.note
            contribution.contributor = request.user
            contribution.save()
            return HttpResponseRedirect('contribution_submitted', pk=contribution.pk)
        return render(request, 'website/contribution/contribution.jinja2', {'form': form})


class ContributionSubmitted(views.APIView):
    template_name = "contribution_submitted.jinja2"
    renderer_classes = (HTMLRenderer, renderers.JSONRenderer)

    def get(self, request, *args, **kwargs):
        contributions = Contribution.objects.order_by('created')[:3]
        contributions_data = ContributionSerializer(contributions,
                                            context={'request': request},
                                            many=True)
        return Response({
            'contributions': contributions_data.data
        })
