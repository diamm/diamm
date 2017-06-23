from django.contrib import admin, messages
from django.shortcuts import render
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from diamm.models.data.geographic_area import GeographicArea
from reversion.admin import VersionAdmin
from diamm.admin.forms.merge_areas import MergeAreasForm
from diamm.admin.merge_models import merge
from salmonella.admin import SalmonellaMixin


@admin.register(GeographicArea)
class GeographicAreaAdmin(SalmonellaMixin, VersionAdmin):
    list_display = ('name', 'area_type', 'get_parent')
    search_fields = ('name',)
    list_filter = ('type',)
    actions = ['merge_areas_action']
    salmonella_fields = ('parent',)

    def get_parent(self, obj):
        if obj.parent:
            return "{0}".format(obj.parent.name)
        return None
    get_parent.short_description = "Parent"

    def merge_areas_action(self, request, queryset):
        if 'do_action' in request.POST:
            form = MergeAreasForm(request.POST)

            if form.is_valid():
                keep_old = form.cleaned_data['keep_old']
                target = queryset.first()
                remainder = list(queryset[1:])
                merged = merge(target, remainder, keep_old=keep_old)

                for archive in merged.archives.all():
                    archive.save()

                for source in merged.protectorate_sources.all():
                    source.save()

                for source in merged.city_sources.all():
                    source.save()

                for source in merged.country_sources.all():
                    source.save()

                for org in merged.organizations.all():
                    org.save()

                messages.success(request, "Objects successfully merged")
                return
            else:
                messages.error(request, 'There was an error merging these organizations')
        else:
            form = MergeAreasForm()

        return render(request,
                      'admin/geographic_area/merge_areas.html', {
                        'objects': queryset,
                        'form': form
                      })
    merge_areas_action.short_description = "Merge Areas"

