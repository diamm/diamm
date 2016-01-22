from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from diamm.models.diamm_user import DIAMMUser


class DIAMMUserInline(admin.StackedInline):
    model = DIAMMUser
    can_delete = False
    verbose_name_plural = "User profile"


class UserAdmin(BaseUserAdmin):
    inlines = (DIAMMUserInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
