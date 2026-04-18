from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fields = ['role', 'phone']


class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'get_role', 'is_active']
    list_filter = ['is_active', 'profile__role']

    def get_role(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.get_role_display()
        return '—'
    get_role.short_description = 'Rol'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'created_at']
    list_filter = ['role']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']


# Re-register User with custom admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
