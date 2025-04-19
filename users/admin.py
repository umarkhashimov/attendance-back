from django.contrib.admin.models import LogEntry
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsersModel, LogAdminActionsModel


class CustomUserAdmin(UserAdmin):
    # Specify the fields in the desired order
    fieldsets = (
        (None, {'fields': ('username', 'password', 'role')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('username', 'password1', 'password2')}),
    )

    # Optionally, you can also customize the list display
    list_display = ('username', 'first_name', 'last_name', 'is_active', 'is_staff', 'role')
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['username', 'first_name', 'last_name']

# Register the CustomUser model with the CustomUserAdmin
admin.site.register(UsersModel, CustomUserAdmin)


# @admin.register(LogEntry)
# class LogEntryAdmin(admin.ModelAdmin):
#     list_display = ('user', 'content_type', 'object_repr', 'action_flag', 'change_message', 'action_time')
#     list_filter = ('action_flag', 'content_type', 'user')
#     search_fields = ('change_message', 'object_repr')


@admin.register(LogAdminActionsModel)
class LogAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_type', 'action_type']
    list_filter = ['user', 'action_number', 'datetime']