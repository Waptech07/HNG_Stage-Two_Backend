from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Organisation

# Register your models here.
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'firstName', 'lastName', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('firstName', 'lastName', 'phone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'firstName', 'lastName', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )
    search_fields = ('email', 'firstName', 'lastName')
    ordering = ('email',)
    filter_horizontal = ()

class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('orgId', 'name')
    search_fields = ('orgId', 'name')


admin.site.register(User, UserAdmin)
admin.site.register(Organisation, OrganisationAdmin)
