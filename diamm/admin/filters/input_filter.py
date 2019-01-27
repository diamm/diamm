from django.contrib.admin import SimpleListFilter


class InputFilter(SimpleListFilter):
    template = "admin/diamm_data/input_filter.html"

    def lookups(self, request, model_admin):
        return (),

    def choices(self, changelist):
        all_choice = next(super().choices(changelist))
        all_choice["query_parts"] = (
            (key, value)
            for key, value in changelist.get_filters_params().items()
            if key != self.parameter_name
        )
        yield all_choice
