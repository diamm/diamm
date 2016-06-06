from django_jinja import library
from diamm.models.site.contribution import Contribution


@library.global_function
def contribution_sort(content_name):
    contributionlist = []
    contributions = Contribution.objects.all().exclude(completed=False)

    for contribution in contributions:
        if contribution.record.__str__() == content_name:
            contributionlist.append(contribution)
    return contributionlist

