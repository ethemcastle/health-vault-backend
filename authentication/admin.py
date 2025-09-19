from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from authentication.models import User


class CustomUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
         ),
    )
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)}),
        (_('Groups'), {'fields': ('groups',)}),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    ordering = ('email',)


if admin.site.is_registered(User):
    admin.site.unregister(User)

admin.site.register(User, CustomUserAdmin)
