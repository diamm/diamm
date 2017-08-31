from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from diamm.models.data.source import Source
from django.conf import settings


class CopyInventoryForm(forms.Form):
    class Media:
        css = {'all': (
            '/static/admin/css/base.css',
            '/static/admin/css/forms.css',
            '/static/admin/css/widgets.css',
        )}
        extra = '' if settings.DEBUG else '.min'
        js = [
            'admin/js/core.js',
            'admin/js/SelectBox.js',
            'admin/js/SelectFilter2.js',
        ]

    def __init__(self, *args, **kwargs):
        self.source_instance = kwargs.pop('instance')
        super().__init__(*args, **kwargs)

    targets = forms.ModelMultipleChoiceField(queryset=Source.objects.all(), widget=FilteredSelectMultiple(verbose_name='Targets', is_stacked=False))
