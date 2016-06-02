from django_jinja import library
from django.contrib.contenttypes.models import ContentType
from diamm.models.site.contribution import Contribution


@library.global_function
def contribution_sort(content_name):
    contributionlist = []
    contributions = Contribution.objects.all().exclude(completed=False)

    for contribution in contributions:
        if contribution.record.__str__() == content_name:
            contributionlist.append(contribution)

    return contributionlist


@library.global_function
def contribution_source_sort(content_name):
    contributionlist = []
    source_content_type = ContentType.objects.get(app_label="diamm_data", model="source")
    contributions = Contribution.objects.filter(content_type=source_content_type)

    for contribution in contributions:
        if contribution.record.display_name.__str__() == content_name:
            contributionlist.append(contribution)

    return contributionlist


