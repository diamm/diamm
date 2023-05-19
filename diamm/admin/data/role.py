from django.contrib import admin

from diamm.models.data.role import Role


# class PersonInline(admin.TabularInline):
#     model = Person
#     extra = 0
#     verbose_name_plural = "People"


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    # inlines = (PersonInline,)

