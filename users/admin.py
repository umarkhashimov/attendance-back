from django.contrib import admin
from .models import UsersModel

# admin.site.register(UsersModel)


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsersModel

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
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')

# Register the CustomUser model with the CustomUserAdmin
admin.site.register(UsersModel, CustomUserAdmin)
