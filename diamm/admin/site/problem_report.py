from django.contrib import admin
from diamm.models.site.problem_report import ProblemReport
from diamm.models.data.person import Person
from diamm.models.data.source import Source
from diamm.models.data.organization import Organization
from diamm.models.data.composition import Composition
from django_extensions.admin import ForeignKeyAutocompleteAdmin


@admin.register(ProblemReport)
class ProblemReportAdmin(ForeignKeyAutocompleteAdmin):
    list_display = ('get_contributor', 'get_entity', 'created', 'completed')
    search_fields = ('contributor__last_name', 'contributor__first_name', 'contributor__username')

    related_search_fields = {
        'contributor': ('last_name', 'first_name', 'username'),
    }

    def get_contributor(self, obj):
        if obj.contributor and obj.contributor.last_name and obj.contributor.first_name:
            return "{0} {1}".format(obj.contributor.first_name, obj.contributor.last_name)
        else:
            return "{0}".format(obj.contributor.username)
    get_contributor.short_description = "contributor"

    def get_entity(self, obj):
        if isinstance(obj.record, Source):
            return "{0} (source)".format(obj.record.display_name)
        elif isinstance(obj.record, Organization):
            return "{0} (organization)".format(obj.record.name)
        elif isinstance(obj.record, Person):
            return "{0} (person)".format(obj.record.full_name)
        elif isinstance(obj.record, Composition):
            return "{0} (composition)".format(obj.record.title)
    get_entity.short_description = "entity"

