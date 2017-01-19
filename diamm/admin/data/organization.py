from django.contrib import admin, messages
from django.shortcuts import render
from diamm.admin.forms.update_organization_type import UpdateOrganizationTypeForm
from diamm.models.data.organization import Organization
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from reversion.admin import VersionAdmin


@admin.register(Organization)
class OrganizationAdmin(VersionAdmin, ForeignKeyAutocompleteAdmin):
    list_display = ('name', 'location', 'type', 'legacy_id')
    list_filter = ('type',)
    search_fields = ('name',)
    actions = ['update_organization_action']

    related_search_fields = {
        'location': ('name', 'parent__name'),
        'archive': ('name', 'city__name')
    }

    def update_organization_action(self, request, queryset):
        if 'do_action' in request.POST:
            form = UpdateOrganizationTypeForm(request.POST)

            if form.is_valid():
                org_type = form.cleaned_data['org_type']
                updated = queryset.update(type=org_type)
                messages.success(request, "{0} organizations were updated.".format(updated))
                return
            else:
                messages.error(request, "There was an error.")
        else:
            form = UpdateOrganizationTypeForm()

        return render(request,
                      'admin/organization/update_organization_type.html', {
                          'objects': queryset,
                          'form': form
                      })

    update_organization_action.short_description = "Update organization type"

